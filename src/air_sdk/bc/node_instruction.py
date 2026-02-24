# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Instruction-specific backward compatibility for v2 SDK.
"""

import json
import warnings
from typing import Any

from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.bc.utils import drop_removed_fields, map_field_names

# Executor type constants
EXECUTOR_SHELL = 'shell'
EXECUTOR_INIT = 'init'
EXECUTOR_FILE = 'file'
VALID_EXECUTORS = {EXECUTOR_SHELL, EXECUTOR_INIT, EXECUTOR_FILE}

# Deprecation messages for each executor type
DEPRECATION_MESSAGES = {
    EXECUTOR_SHELL: "data={'commands': ['your command']}",
    EXECUTOR_INIT: "data={'hostname': 'your-hostname'}",
    EXECUTOR_FILE: (
        "data={'files': [{'path': '/path', 'content': 'content'}], "
        "'post_commands': ['cmd']}"
    ),
}


def _convert_data_field_to_dict(kwargs: dict[str, Any]) -> None:
    """Convert V2's string 'data' parameter to V3's dict format based on executor type.

    V2 accepted a string for 'data' regardless of executor type.
    V3 requires structured dicts based on executor:
    - 'shell': {'commands': [str, ...]}
    - 'file': {'files': [{'path': str, 'content': str}, ...], 'post_commands': [str, ...]}
    - 'init': {'hostname': str}
    """
    data_str = kwargs['data']
    executor = kwargs.get('executor')

    # If executor is not specified, we cannot convert - let it fail naturally
    if executor is None:
        return

    # Issue single deprecation warning with dynamic message
    if executor in VALID_EXECUTORS:
        warnings.warn(
            f"Passing 'data' as a string for '{executor}' executor is deprecated. "
            f'Use a dict instead: {DEPRECATION_MESSAGES[executor]}',
            DeprecationWarning,
            stacklevel=3,
        )

    if executor == EXECUTOR_SHELL:
        kwargs['data'] = {'commands': [data_str]}
    elif executor == EXECUTOR_INIT:
        kwargs['data'] = {'hostname': data_str}
    elif executor == EXECUTOR_FILE:
        try:
            # Try to parse as JSON (V2 format with file paths and content)
            v2_data = json.loads(data_str)

            # Extract post_cmd if present
            post_cmd = v2_data.pop('post_cmd', None)

            # Validate exactly one file is included
            if len(v2_data) != 1:
                raise ValueError(
                    "Invalid 'file' executor data: must include exactly one file. "
                    "V2 format: {'<file_path>': '<content>'} or "
                    "{'<file_path>': '<content>', 'post_cmd': '<command>'}"
                )

            # Convert remaining entry to files list
            files = [
                {'path': path, 'content': content} for path, content in v2_data.items()
            ]

            # Build V3 format
            v3_data: dict[str, Any] = {'files': files}
            if post_cmd:
                if isinstance(post_cmd, str):
                    v3_data['post_commands'] = [post_cmd]
                elif isinstance(post_cmd, list):
                    v3_data['post_commands'] = post_cmd
                else:
                    raise ValueError(
                        'Invalid `post_cmd` type: must be a string or list of strings'
                    )

            kwargs['data'] = v3_data
        except (json.JSONDecodeError, AttributeError) as e:
            raise ValueError(
                "Invalid 'file' executor data: must be valid JSON. "
                "V2 format: {'<file_path>': '<content>'} or "
                "{'<file_path>': '<content>', 'post_cmd': '<command>'}"
            ) from e


class NodeInstructionCompatMixin(AirModelCompatMixin):
    """Mixin providing NodeInstruction-specific v2 SDK backward compatibility.

    This maintains compatibility with NodeInstruction fields and methods from older
    SDK versions:
    - Field mappings: instruction → data (with string → dict conversion)
    - Removed fields: monitor
    """

    # Module-level field mappings: old (v2) → new (v3)
    _FIELD_MAPPINGS: dict[str, str] = {
        'instruction': 'data',  # v2's 'instruction' string → v3's 'data' dict
    }

    # Fields and filters that were removed in v3
    _REMOVED_FIELDS = ['monitor']

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update method with field name compatibility for Instructions."""
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(kwargs, self._REMOVED_FIELDS)
        map_field_names(kwargs, self._FIELD_MAPPINGS)

        # handle the case where the user tries to update the data of the instruction
        if 'data' in kwargs:
            warnings.warn(
                'The data of an instruction cannot be updated in the current '
                'AIR API version.',
                DeprecationWarning,
                stacklevel=3,
            )

        super().update(*args, **kwargs)  # type: ignore[misc]


class NodeInstructionEndpointAPICompatMixin:
    """Mixin providing API-level backward compatibility for Instruction endpoints.

    This handles BC for API-level methods (create, list, etc.)
    where v2 used different parameter or field names than v3:
    - instruction (string) → data (dict) (type change)
    - monitor removed
    """

    def create(self, *args: Any, **kwargs: Any) -> Any:
        """Create method with v2 → v3 compatibility.

        Handles:
        - data: str → data: dict conversion
        - pk: str → node: str (node ID)
        - Drops monitor fields
        """
        drop_removed_fields(kwargs, NodeInstructionCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, NodeInstructionCompatMixin._FIELD_MAPPINGS)

        # handle the case where the user tries to create the instruction with the pk field
        if 'pk' in kwargs:
            kwargs['node'] = kwargs.pop('pk')

        if 'data' in kwargs and isinstance(kwargs['data'], str):
            _convert_data_field_to_dict(kwargs)

        return super().create(*args, **kwargs)  # type: ignore[misc]

    def list(self, *args: Any, **kwargs: Any) -> Any:
        """List method with v2 → v3 compatibility.

        Handles:
        - Drops monitor field
        """
        drop_removed_fields(kwargs, NodeInstructionCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, NodeInstructionCompatMixin._FIELD_MAPPINGS)

        return super().list(*args, **kwargs)  # type: ignore[misc]

    def patch(self, *args: Any, **kwargs: Any) -> Any:
        """Patch a node instruction with v2 → v3 compatibility.

        Handles:
        - Drops monitor field
        """
        drop_removed_fields(kwargs, NodeInstructionCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, NodeInstructionCompatMixin._FIELD_MAPPINGS)

        # handle the case where the user tries to update the data of the instruction
        if 'data' in kwargs:
            warnings.warn(
                'The data of an instruction cannot be updated in the current '
                'AIR API version.',
                DeprecationWarning,
                stacklevel=3,
            )

        return super().patch(*args, **kwargs)  # type: ignore[misc]
