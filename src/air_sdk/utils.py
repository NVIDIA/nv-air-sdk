# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import inspect
import re
import time
from dataclasses import _MISSING_TYPE, Field, fields, is_dataclass
from datetime import datetime, timedelta, timezone
from functools import wraps
from http import HTTPStatus
from json import JSONDecodeError
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Callable,
    Optional,
    TypeVar,
    cast,
    get_type_hints,
)
from urllib.parse import ParseResult, urlparse
from uuid import UUID, uuid4

from requests import Response

from air_sdk.exceptions import AirUnexpectedResponse
from air_sdk.types import type_check

if TYPE_CHECKING:
    from air_sdk.air_model import AirModel

F = TypeVar('F', bound=Callable[..., Any])


def filter_missing(**kwargs: Any) -> dict[str, Any]:
    """Filter out MISSING values from kwargs.

    This is a helper function to remove dataclasses.MISSING sentinel values
    before passing kwargs to API methods.

    Args:
        **kwargs: Keyword arguments that may contain MISSING values

    Returns:
        Dictionary with MISSING values filtered out
    """
    return {k: v for k, v in kwargs.items() if not isinstance(v, _MISSING_TYPE)}


# Mapping of string type names to actual builtin types
BUILTIN_TYPES = {
    'str': str,
    'int': int,
    'bool': bool,
    'float': float,
    'dict': dict,
    'list': list,
    'tuple': tuple,
    'set': set,
}

API_URI_PATTERN = r'^/api/v\d+.*$'
COMPILED_API_URI_PATTERN = re.compile(API_URI_PATTERN)


def join_urls(*args: str) -> str:
    return '/'.join(frag.strip('/') for frag in args) + '/'


def iso_string_to_datetime(iso: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(iso.replace('Z', '+00:00'))
    except ValueError:
        return None


def datetime_to_iso_string(date: datetime) -> str:
    """Convert datetime to ISO string in UTC.

    Accepts any timezone-aware datetime. For naive datetimes (no timezone),
    assumes local timezone and emits a warning.

    Args:
        date: The datetime to convert

    Returns:
        ISO 8601 formatted string in UTC (with 'Z' suffix)

    Warns:
        UserWarning: If datetime is naive (no timezone specified)
    """
    import warnings

    # Handle naive datetimes by assuming local timezone and warning
    if date.tzinfo is None:
        warnings.warn(
            'Naive datetime provided. '
            'Assuming local timezone. '
            'Use datetime.now(timezone.utc) for explicit UTC times.',
            UserWarning,
            stacklevel=2,
        )
        # Assume local timezone
        date = date.astimezone()

    return date.astimezone(tz=timezone.utc).isoformat().replace('+00:00', 'Z')


def to_uuid(uuid: str) -> Optional[UUID]:
    try:
        return UUID(uuid, version=4)
    except ValueError:
        return None


def to_url(url: str) -> Optional[ParseResult]:
    try:
        parsed_url = urlparse(url)
        return (
            parsed_url
            if all((parsed_url.scheme, parsed_url.netloc, parsed_url.path))
            else None
        )
    except AttributeError:
        return None


def is_dunder(name: str) -> bool:
    delimiter = '__'
    return name.startswith(delimiter) and name.endswith(delimiter)


def as_field(class_or_instance: object, name: str) -> Optional[Field]:  # type: ignore[type-arg]
    if is_dataclass(class_or_instance):
        try:
            return next(
                field for field in fields(class_or_instance) if field.name == name
            )
        except StopIteration:
            pass
    return None


def _resolve_type_hints_fallback(func: Callable[..., Any]) -> dict[str, Any]:
    """
    Fallback type hint resolution when get_type_hints() fails.

    This handles cases where TYPE_CHECKING imports aren't available at runtime.
    Only validates types that can be resolved at runtime.

    Args:
        func: Function to extract type hints from

    Returns:
        Dictionary of resolvable type hints (name -> type)
    """
    hints: dict[str, Any] = {}
    raw_annotations = getattr(func, '__annotations__', {})

    for name, annotation in raw_annotations.items():
        # Skip return type
        if name == 'return':
            continue

        # Try to resolve each annotation individually
        try:
            if isinstance(annotation, str):
                # Try basic type resolution from builtins
                if annotation in BUILTIN_TYPES:
                    hints[name] = BUILTIN_TYPES[annotation]
                elif annotation == 'Any':
                    hints[name] = Any
                # Otherwise, skip (likely a TYPE_CHECKING import)
            elif hasattr(annotation, '__origin__'):
                # Generic type like dict[str, Any]
                hints[name] = annotation
            elif inspect.isclass(annotation):
                # Real class
                hints[name] = annotation
        except Exception:
            # Can't resolve - skip validation for this parameter
            continue

    return hints


def validate_payload_types(func: F) -> F:
    """A wrapper for validating the type of payload during create."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # Try to get type hints with proper resolution
            hints = get_type_hints(func)
        except NameError:
            # TYPE_CHECKING imports aren't available at runtime
            # Use fallback to resolve only available types
            hints = _resolve_type_hints_fallback(func)

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for name, value in bound_args.arguments.items():
            if name in hints:
                expected_type = hints[name]
                if not type_check(value, expected_type):
                    raise TypeError(
                        f"Argument '{name}' must be {expected_type}, got {type(value)}"
                    )

        return func(*args, **kwargs)

    return cast(F, wrapper)


def sha256_file(path: str | Path) -> str:
    """Get the SHA256 hash of the local file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()


def calculate_multipart_info(file_size: int, chunk_size: int) -> list[dict[str, int]]:
    """Calculate part information for multipart upload.

    Args:
        file_size: Total size of the file in bytes
        chunk_size: Size of each chunk in bytes

    Returns:
        List of dictionaries containing part info with keys:
        - part_number: 1-based part number
        - start: Start byte offset
        - size: Size of this part in bytes
    """
    parts = []
    part_number = 1
    offset = 0

    while offset < file_size:
        part_size = min(chunk_size, file_size - offset)
        parts.append({'part_number': part_number, 'start': offset, 'size': part_size})
        offset += part_size
        part_number += 1

    return parts


class FilePartReader:
    """File-like object that reads only a specific portion of a file.

    Used for streaming multipart uploads without loading entire file into memory.
    This class implements the context manager protocol and provides a read()
    method compatible with requests streaming uploads.

    Args:
        file_path: Path to the file to read from
        start: Starting byte offset in the file
        size: Number of bytes to read from the start offset

    Example:
        >>> with FilePartReader('large_file.bin', start=0, size=5242880) as reader:
        ...     requests.put(presigned_url, data=reader)
    """

    def __init__(self, file_path: str | Path, start: int, size: int):
        self.file_path = file_path
        self.start = start
        self.size = size
        self.remaining = size
        self.f: BinaryIO | None = None

    def __enter__(self) -> 'FilePartReader':
        self.f = open(self.file_path, 'rb')
        self.f.seek(self.start)
        return self

    def __exit__(self, *args: Any) -> None:
        if self.f:
            self.f.close()

    def __len__(self) -> int:
        """Return the total size of this part.

        This is required for requests to set Content-Length header
        instead of using Transfer-Encoding: chunked (which S3 doesn't support).
        """
        return self.size

    def read(self, chunk_size: int = -1) -> bytes:
        """Read up to chunk_size bytes, but never exceed the part size.

        Args:
            chunk_size: Number of bytes to read. If -1, reads remaining bytes.

        Returns:
            Bytes read from the file, up to the specified chunk size
        """
        if self.remaining <= 0:
            return b''

        if not self.f:
            raise RuntimeError(
                'FilePartReader must be used within a context manager '
                '(with FilePartReader(...) as reader:)'
            )

        if chunk_size < 0:
            chunk_size = self.remaining
        else:
            chunk_size = min(chunk_size, self.remaining)

        data = self.f.read(chunk_size)
        self.remaining -= len(data)
        return data


def create_short_uuid() -> str:
    return str(uuid4()).replace('-', '')[:18]


def normalize_api_url(url: str) -> str:
    """Ensures the API URL ends with the correct path."""
    parsed_url = urlparse(url)
    if not COMPILED_API_URI_PATTERN.match(parsed_url.path):
        parsed_url = parsed_url._replace(path='/api/v3')
    return parsed_url.geturl()


def raise_if_invalid_response(
    res: Response, status_code: HTTPStatus = HTTPStatus.OK, data_type: type | None = dict
) -> None:
    """
    Validates that a given API response has the expected status code and JSON payload

    Arguments:
    res (requests.HTTPResponse) - API response object
    status_code [int] - Expected status code (default: 200)

    Raises:
    AirUnexpectedResponse - Raised if an unexpected response is received from the API
    """
    json = None
    if res.status_code != status_code:
        # logger.debug(res.text)
        raise AirUnexpectedResponse(message=res.text, status_code=res.status_code)
    if not data_type:
        return
    try:
        json = res.json()
    except JSONDecodeError:
        raise AirUnexpectedResponse(message=res.text, status_code=res.status_code)
    if not isinstance(json, data_type):
        raise AirUnexpectedResponse(
            message=f'Expected API response to be of type {data_type}, '
            + f'got {type(json)}',
            status_code=res.status_code,
        )


def wait_for_state(
    model: AirModel,
    target_states: str | list[str],
    *,
    state_field: str = 'state',
    timeout: timedelta | None = None,
    poll_interval: timedelta | None = None,
    error_states: str | list[str] | None = None,
) -> None:
    """Wait for a model to reach one of the target states.

    This is a generic utility that works with any AirModel that has a state field
    (e.g., Simulation.state, Node.state, Image.upload_status, etc.).

    Args:
        model: The AirModel instance to monitor (Simulation, Node, Image, etc.)
        target_states: Single state or list of states to wait for
        state_field: Name of the field containing the state (default: 'state').
                    Use 'upload_status' for Images, 'state' for most other models.
        timeout: Maximum time to wait (default: 120 seconds)
        poll_interval: Time between status checks (default: 2 seconds)
        error_states: Single state or list of states that should raise an error.
                     If None, no error states are checked.

    Raises:
        ValueError: If the model enters one of the error states
        TimeoutError: If timeout is reached before target state
        AttributeError: If the model doesn't have the specified state_field

    Example:
        >>> # Wait for simulation to become active
        >>> wait_for_state(simulation, 'ACTIVE', error_states=['INVALID', 'DELETING'])
        >>>
        >>> # Wait for image upload to complete
        >>> wait_for_state(image, 'COMPLETE', state_field='upload_status')
        >>>
        >>> # Wait for node to boot or become active
        >>> wait_for_state(node, ['BOOTING', 'ACTIVE'], error_states='ERROR')
    """
    # Set defaults
    if timeout is None:
        timeout = timedelta(seconds=120)
    if poll_interval is None:
        poll_interval = timedelta(seconds=2)

    # Normalize to lists
    if isinstance(target_states, str):
        target_states = [target_states]
    if isinstance(error_states, str):
        error_states = [error_states]
    elif error_states is None:
        error_states = []

    # Validate that the model has the specified state field
    if not hasattr(model, state_field):
        raise AttributeError(
            f'Model {type(model).__name__} does not have a "{state_field}" field. '
            f'Available fields: {", ".join(f.name for f in fields(model))}'
        )

    start_time = time.time()
    timeout_seconds = timeout.total_seconds()
    poll_interval_seconds = poll_interval.total_seconds()
    end_time = start_time + timeout_seconds

    while time.time() < end_time:
        model.refresh()
        current_state = getattr(model, state_field)

        if current_state in target_states:
            return

        if current_state in error_states:
            model_type = type(model).__name__
            raise ValueError(
                f'{model_type} entered error state: {current_state}. '
                f'Please check the {model_type.lower()} for more details.'
            )

        # Wait before polling again
        time.sleep(poll_interval_seconds)

    # Timeout reached
    current_state = getattr(model, state_field)
    states_str = ', '.join(target_states)
    model_type = type(model).__name__
    raise TimeoutError(
        f'Timed out waiting for {model_type} to reach state(s): {states_str}. '
        f'Current {state_field}: {current_state}'
    )
