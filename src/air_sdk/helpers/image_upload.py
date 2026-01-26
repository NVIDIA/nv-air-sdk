# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
"""
Helper functions for image upload operations.

This module contains the implementation of image upload workflows
for the ImageEndpointAPI. These functions are separated from the main endpoint
implementation to improve code organization and testability.
"""

from __future__ import annotations

import os
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import requests

from air_sdk.const import (
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_RETRY_BACKOFF_FACTOR,
    DEFAULT_UPLOAD_TIMEOUT,
    MULTIPART_CHUNK_SIZE,
    MULTIPART_MIN_PART_SIZE,
)
from air_sdk.endpoints import mixins
from air_sdk.exceptions import AirUnexpectedResponse
from air_sdk.utils import (
    FilePartReader,
    join_urls,
    raise_if_invalid_response,
    sha256_file,
)

if TYPE_CHECKING:
    from air_sdk import AirAPI
    from air_sdk.endpoints.images import Image


def abort_multipart_upload(
    *,
    api_client: AirAPI,
    base_url: str,
    image: Image,
) -> None:
    """Abort a multipart upload to clean up S3 resources.

    This should be called when a multipart upload fails to prevent
    orphaned uploads in S3 storage.

    Args:
        api_client: The AirApi client instance for making HTTP requests
        base_url: Base URL for the images endpoint
        image: Image instance (must be in UPLOADING status)

    Note:
        This method does not raise exceptions on failure, as it's meant
        for cleanup during error handling. Warnings are issued instead.
    """
    try:
        abort_url = join_urls(base_url, str(image.id), 'abort-upload')

        abort_response = api_client.client.patch(abort_url, data='{}')

        # Expect 204 No Content on success
        if abort_response.status_code != HTTPStatus.NO_CONTENT:
            warnings.warn(
                f'Failed to abort multipart upload '
                f'for image {image.id}: HTTP {abort_response.status_code}. ',
                stacklevel=3,
            )
    except Exception as e:
        # Catch all exceptions to prevent masking the original error
        warnings.warn(
            f'Exception while aborting multipart upload for image {image.id}: {e}. ',
            stacklevel=3,
        )


def upload_single_part(
    *,
    api_client: AirAPI,
    filepath: str | Path,
    part_number: int,
    start_offset: int,
    part_size: int,
    presigned_url: str,
    timeout: float,
    max_retries: int = DEFAULT_RETRY_ATTEMPTS,
) -> dict[str, Any]:
    """Upload a single part to S3 with retry logic for transient failures.

    Automatically retries on transient network errors (connection errors,
    timeouts, 503/429 responses) with exponential backoff. Non-transient
    errors are raised immediately.

    Args:
        api_client: The AirApi client instance (used for verify setting)
        filepath: Path to the file to upload
        part_number: Part number (1-indexed)
        start_offset: Starting byte offset in file
        part_size: Size of this part in bytes
        presigned_url: S3 presigned URL for this part
        timeout: Timeout in seconds for the upload
        max_retries: Maximum number of retry attempts
            (default: DEFAULT_RETRY_ATTEMPTS)

    Returns:
        Dict with 'part_number' and 'etag' keys

    Raises:
        AirUnexpectedResponse: If upload fails or S3 doesn't return ETag
        requests.RequestException: If all retry attempts fail
    """
    last_exception: Exception | None = None
    upload_response: requests.Response | None = None

    for attempt in range(max_retries):
        retry_reason = None  # Will be set if we should retry
        last_exception = None  # Reset each attempt to track the current failure

        try:
            with FilePartReader(filepath, start_offset, part_size) as part_reader:
                upload_response = requests.put(
                    presigned_url,
                    data=part_reader,
                    timeout=timeout,
                    verify=api_client.client.verify,
                )

                # Check for transient HTTP errors that should be retried
                # 429: Too Many Requests (rate limiting)
                # 502: Bad Gateway (upstream server error)
                # 503: Service Unavailable (temporary overload/maintenance)
                # 504: Gateway Timeout (upstream timeout)
                if upload_response.status_code in (429, 502, 503, 504):
                    retry_reason = f'HTTP {upload_response.status_code}'
                else:
                    # Not a transient error - validate the response
                    raise_if_invalid_response(
                        upload_response, status_code=HTTPStatus.OK, data_type=None
                    )

                    etag = upload_response.headers.get('ETag', '').strip('"')
                    if not etag:
                        raise AirUnexpectedResponse(
                            f'S3 did not return ETag for part {part_number}. '
                            f'Upload may have failed silently.'
                        )
                    return {'part_number': part_number, 'etag': etag}

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
        ) as e:
            last_exception = e
            retry_reason = f'{type(e).__name__}: {e}'

        except Exception:
            # Don't retry on non-transient errors
            # (e.g., file not found, invalid response)
            raise

        # Common retry logic
        if retry_reason:
            if attempt < max_retries - 1:
                wait_time = DEFAULT_RETRY_BACKOFF_FACTOR * (2**attempt)
                warnings.warn(
                    f'Part {part_number} upload failed ({retry_reason}). '
                    f'Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})',
                    stacklevel=4,
                )
                time.sleep(wait_time)
                continue
            else:
                # Last attempt - raise the appropriate error
                if last_exception:
                    raise last_exception
                # For HTTP errors, validate response to raise proper error
                # upload_response is guaranteed to exist here since we only
                # reach this path after receiving an HTTP response
                assert upload_response is not None
                raise_if_invalid_response(
                    upload_response, status_code=HTTPStatus.OK, data_type=None
                )

    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise AirUnexpectedResponse(
        f'Part {part_number} upload failed after {max_retries} attempts'
    )


def upload_parts_to_s3(
    *,
    api_client: AirAPI,
    filepath: str | Path,
    parts_info: list[dict[str, int]],
    part_urls: list[dict[str, Any]],
    timeout_per_part: float,
    max_workers: int = 1,
) -> list[dict[str, Any]]:
    """Upload file parts directly to S3 using presigned URLs.

    Supports both sequential (max_workers=1) and parallel (max_workers>1) uploads.

    Args:
        api_client: The AirApi client instance
        filepath: Path to the file to upload
        parts_info: List of part information (part_number, start, size)
        part_urls: List of presigned URL data from backend
        timeout_per_part: Timeout in seconds for each part upload
        max_workers: Number of concurrent upload workers. Default: 1 (sequential)

    Returns:
        List of uploaded parts with part_number and etag, sorted by part_number

    Raises:
        AirUnexpectedResponse: If any part upload fails
    """
    if max_workers == 1:
        # Sequential upload (default)
        uploaded_parts = []
        for part_info, part_url_data in zip(parts_info, part_urls):
            result = upload_single_part(
                api_client=api_client,
                filepath=filepath,
                part_number=part_info['part_number'],
                start_offset=part_info['start'],
                part_size=part_info['size'],
                presigned_url=part_url_data['url'],
                timeout=timeout_per_part,
            )
            uploaded_parts.append(result)

        # Sort by part number to ensure correct order
        uploaded_parts.sort(key=lambda x: x['part_number'])
        return uploaded_parts

    # Parallel upload
    uploaded_parts = []
    failed_parts = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all upload tasks
        future_to_part = {}
        for part_info, part_url_data in zip(parts_info, part_urls):
            future = executor.submit(
                upload_single_part,
                api_client=api_client,
                filepath=filepath,
                part_number=part_info['part_number'],
                start_offset=part_info['start'],
                part_size=part_info['size'],
                presigned_url=part_url_data['url'],
                timeout=timeout_per_part,
            )
            future_to_part[future] = part_info['part_number']

        # Collect results as they complete
        try:
            for future in as_completed(future_to_part):
                part_number = future_to_part[future]
                try:
                    result = future.result()
                    uploaded_parts.append(result)
                except Exception as e:
                    # Part upload failed - cancel remaining uploads to save bandwidth
                    failed_parts.append((part_number, str(e)))
                    for f in future_to_part:
                        if not f.done():
                            f.cancel()
                    break  # Stop collecting results
        except Exception:
            # On unexpected error during result collection, cancel any pending futures
            # to avoid leaving orphaned threads running
            for future in future_to_part:
                future.cancel()
            raise

    # Check if all parts uploaded successfully
    if failed_parts:
        error_msg = 'Failed to upload the following parts:\n'
        for part_num, error in failed_parts:
            error_msg += f'  Part {part_num}: {error}\n'
        raise AirUnexpectedResponse(error_msg)

    # Sort by part number to ensure correct order
    uploaded_parts.sort(key=lambda x: x['part_number'])
    return uploaded_parts


def complete_multipart_upload(
    *,
    api_client: AirAPI,
    base_url: str,
    image: Image,
    uploaded_parts: list[dict[str, Any]],
) -> None:
    """Complete a multipart upload by sending ETags to backend.

    Backend will use boto3.complete_multipart_upload() with the ETags.

    Args:
        api_client: The AirApi client instance for making HTTP requests
        base_url: Base URL for the images endpoint
        image: Image instance
        uploaded_parts: List of uploaded parts with part_number and etag

    Raises:
        requests.RequestException: If completion fails
    """
    complete_payload = {
        'parts': uploaded_parts,
    }
    complete_upload_url = join_urls(base_url, str(image.id), 'complete-upload')
    complete_upload_response = api_client.client.patch(
        complete_upload_url, data=mixins.serialize_payload(complete_payload)
    )
    raise_if_invalid_response(complete_upload_response, status_code=HTTPStatus.OK)
    image.refresh()


def calculate_parts_info(
    file_size: int,
    num_parts: int,
    chunk_size: int,
) -> list[dict[str, int]]:
    """Calculate byte ranges for each part based on file size and number of parts.

    The API determines the number of parts and chunk size automatically.
    This function calculates the actual byte ranges for each part.

    Args:
        file_size: Total file size in bytes
        num_parts: Number of parts (from API response)
        chunk_size: Size of each chunk in bytes (from API response)

    Returns:
        List of dicts with part_number, start, and size for each part
    """
    if num_parts == 0:
        return []

    parts_info = []
    for i in range(num_parts):
        part_number = i + 1  # Parts are 1-indexed
        start = i * chunk_size
        is_last_part = i == num_parts - 1

        if is_last_part:
            # Last part gets whatever remains
            size = file_size - start
        else:
            size = chunk_size

        # Validate part size
        if size <= 0:
            raise AirUnexpectedResponse(
                f'Part {part_number} has invalid size ({size} bytes). '
                f'The backend returned too many parts ({num_parts}) for '
                f'file size ({file_size} bytes).'
            )

        # S3 requires all parts except the last to be at least 5 MiB
        if not is_last_part and size < MULTIPART_MIN_PART_SIZE:
            raise AirUnexpectedResponse(
                f'Part {part_number} size ({size} bytes) is below S3 minimum '
                f'of {MULTIPART_MIN_PART_SIZE} bytes (5 MiB). The backend returned '
                f'too many parts ({num_parts}) for file size ({file_size} bytes).'
            )

        parts_info.append(
            {
                'part_number': part_number,
                'start': start,
                'size': size,
            }
        )
    return parts_info


def upload_image(
    *,
    api_client: AirAPI,
    base_url: str,
    image: Image,
    filepath: str | Path,
    timeout: Optional[timedelta] = None,
    max_workers: int = 1,
    **kwargs: Any,
) -> 'Image':
    """Upload an image file using multipart upload.

    All uploads use multipart upload to S3. The API calculates parts (~100MB each)
    automatically based on file size.

    The upload flow is:
    1. Start upload with hash and size → get upload_id and presigned URLs
    2. Upload each part directly to S3 using presigned URLs
    3. Complete upload with part ETags

    If any step fails, the multipart upload is automatically aborted to prevent
    orphaned data in S3 storage.

    Args:
        api_client: The AirApi client instance for making HTTP requests
        base_url: Base URL for the images endpoint
        image: Image instance
        filepath: Path to the file to upload
        timeout: Timeout per part upload
            (default: DEFAULT_UPLOAD_TIMEOUT = 5 minutes).
            This timeout applies to EACH part, not the entire multipart
            operation.
        max_workers: Number of concurrent upload workers. Default: 1 (sequential).
            Set > 1 for parallel uploads (e.g., 4 for 4 concurrent uploads).
        **kwargs: Additional arguments (currently unused, kept for API compatibility)

    Note:
        Presigned URL expiration varies by file size. Check the backend
        documentation for the exact expiration time.

    Returns:
        Updated Image instance

    Raises:
        AirUnexpectedResponse: If upload fails or backend returns invalid data
        Exception: For other upload errors
    """
    file_size = os.path.getsize(filepath)

    # Use the provided timeout (or default) for each part upload
    # This ensures sufficient time for large parts without dividing by part count
    timeout = timeout or DEFAULT_UPLOAD_TIMEOUT
    timeout_per_part = timeout.total_seconds()

    # Step 1: Get the file hash and initiate multipart upload
    file_hash = sha256_file(filepath)
    payload = {
        'hash': file_hash,
        'size': file_size,
    }

    start_upload_url = join_urls(base_url, str(image.id), 'start-upload')
    start_upload_response = api_client.client.patch(
        start_upload_url, data=mixins.serialize_payload(payload)
    )
    raise_if_invalid_response(start_upload_response, status_code=HTTPStatus.OK)
    image.refresh()

    # Get presigned URLs and chunk size from backend
    response_data = start_upload_response.json()
    upload_id = response_data.get('upload_id')
    part_urls = response_data.get('part_urls', [])
    chunk_size = response_data.get('chunk_size', MULTIPART_CHUNK_SIZE)

    # Validate backend response before proceeding
    if not upload_id:
        raise AirUnexpectedResponse(
            'Backend did not return upload_id for multipart upload. '
            'This indicates a server error.'
        )

    # Step 2-3: Upload parts and complete with cleanup on failure
    # Wrap everything after upload_id is obtained to ensure cleanup on any failure
    try:
        if not part_urls:
            raise AirUnexpectedResponse(
                'Backend did not return presigned URLs for multipart upload. '
                'This indicates a server error.'
            )

        # Calculate part byte ranges based on number of parts and chunk size from API
        parts_info = calculate_parts_info(file_size, len(part_urls), chunk_size)

        # Step 2: Upload each part directly to S3 using presigned URLs
        uploaded_parts = upload_parts_to_s3(
            api_client=api_client,
            filepath=filepath,
            parts_info=parts_info,
            part_urls=part_urls,
            timeout_per_part=timeout_per_part,
            max_workers=max_workers,
        )

        # Step 3: Complete the multipart upload
        complete_multipart_upload(
            api_client=api_client,
            base_url=base_url,
            image=image,
            uploaded_parts=uploaded_parts,
        )

        return image

    except Exception:
        # Cleanup: abort the multipart upload to prevent orphaned S3 data
        abort_multipart_upload(api_client=api_client, base_url=base_url, image=image)
        # Re-raise the original exception
        raise
