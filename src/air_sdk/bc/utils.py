# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Utility functions for backward compatibility layer.
"""

import inspect
import warnings
from typing import Any, Callable


# NOTE: This function is currently not in use because we use .pyi stub files
# for type hints, which means inspect.signature() cannot extract the actual
# runtime function signatures. Keeping this for potential future use if we
# need positional-to-keyword argument mapping for BC.
def map_positional_args(
    func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Map positional arguments to keyword arguments based on function signature.

    This utility helps maintain backward compatibility when transitioning from
    positional to keyword-only arguments.

    Args:
        func: The function to inspect
        args: Positional arguments provided
        kwargs: Keyword arguments provided

    Returns:
        Dictionary with all arguments as keyword arguments

    Example:
        >>> def my_func(*, name: str, value: int = 10):
        >>>     pass
        >>> map_positional_args(my_func, ('test', 20), {})
        {'name': 'test', 'value': 20}
        >>> map_positional_args(my_func, ('test',), {'value': 20})
        {'name': 'test', 'value': 20}
    """
    sig = inspect.signature(func)
    param_names = [
        p.name for p in sig.parameters.values() if p.name not in ('self', 'cls')
    ]

    # Map positional args to param names
    mapped = dict(zip(param_names, args))
    # Merge with kwargs (kwargs take precedence)
    mapped.update(kwargs)

    return mapped


def drop_removed_fields(
    kwargs: dict[str, Any],
    removed_fields: list[str],
    critical_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
    stacklevel: int = 4,
) -> None:
    # fmt: off
    """Drop fields that were removed in v3 and warn user.

    Args:
        kwargs: Dictionary of keyword arguments to modify in-place
        removed_fields: List of field names that are not supported (will warn)
        critical_fields: List of field names that will raise an exception if present
        exclude_fields: List of field names to keep even if in removed_fields
        stacklevel: Stack level for the warning (default: 4)

    Raises:
        ValueError: If any critical_fields are present in kwargs

    Example:
        >>> # Warn and drop non-critical fields
        >>> kwargs = {'name': 'test', 'metadata': 'old'}
        >>> drop_removed_fields(kwargs, ['metadata'])
        >>> kwargs
        {'name': 'test'}

        >>> # Keep specific fields even if in removed_fields
        >>> kwargs = {'name': 'test', 'simulation': '123', 'metadata': 'old'}
        >>> drop_removed_fields(
        ...     kwargs, ['simulation', 'metadata'], exclude_fields=['simulation']
        ... )
        >>> kwargs
        {'name': 'test', 'simulation': '123'}

       >>> # Keep specific fields even if in removed_fields
        >>> kwargs = {'name': 'test', 'simulation': '123', 'metadata': 'old'}
        >>> drop_removed_fields(
        ...     kwargs, ['simulation', 'metadata'], exclude_fields=['simulation']
        ... )
        >>> kwargs
        {'name': 'test', 'simulation': '123'}


        >>> # Raise exception for critical fields
        >>> kwargs = {'name': 'test', 'critical_param': 'value'}
        >>> drop_removed_fields(kwargs, [], critical_fields=['critical_param'])
        Traceback (most recent call last):
        ...
        ValueError: ... not supported in the current air-api ... 'critical_param' ...
    """
    # fmt: on
    # Check for critical fields first (raise exception)
    if critical_fields:
        found_critical = [field for field in critical_fields if field in kwargs]
        if found_critical:
            fields_str = ', '.join(f"'{field}'" for field in found_critical)
            raise ValueError(
                f'The following parameters are not supported in the current '
                f'air-api version and cannot be used: {fields_str}. These parameters '
                f'had critical functionality in older air-api versions that is no '
                f'longer available. Please remove them from your call.'
            )

    # Build the list of fields to actually drop (excluding specified fields)
    exclude_set = set(exclude_fields) if exclude_fields else set()
    fields_to_drop = [field for field in removed_fields if field not in exclude_set]

    # Drop non-critical removed fields and warn
    dropped_fields = []
    for field in fields_to_drop:
        if field in kwargs:
            kwargs.pop(field)
            dropped_fields.append(field)

    if dropped_fields:
        dropped_fields_str = ', '.join(f"'{field}'" for field in dropped_fields)
        warnings.warn(
            f'The following parameters are not supported in the current air-api '
            f'version and will be ignored: {dropped_fields_str}. '
            f'These parameters were available in older air-api versions.',
            DeprecationWarning,
            stacklevel=stacklevel,
        )


def map_field_names(
    kwargs: dict[str, Any],
    field_mappings: dict[str, str],
    stacklevel: int = 4,
) -> None:
    """Map v1/v2 field names to v3 equivalents.

    Args:
        kwargs: Dictionary of keyword arguments to modify in-place
        field_mappings: Dictionary mapping old field names to new ones
        stacklevel: Stack level for the warning (default: 4)

    Example:
        >>> kwargs = {'title': 'My Sim', 'owner': 'user@example.com'}
        >>> mappings = {'title': 'name', 'owner': 'creator'}
        >>> map_field_names(kwargs, mappings)
        >>> kwargs
        {'name': 'My Sim', 'creator': 'user@example.com'}
    """
    for old_name, new_name in field_mappings.items():
        if old_name in kwargs:
            warnings.warn(
                f'The field name "{old_name}" has been changed to "{new_name}" in the '
                f'current air-api version. Please update your code to use the new name.',
                DeprecationWarning,
                stacklevel=stacklevel,
            )
            kwargs[new_name] = kwargs.pop(old_name)


def handle_boolean_datetime_fields(
    kwargs: dict[str, Any],
    field_mappings: dict[str, str],
    stacklevel: int = 4,
) -> None:
    """Handle boolean fields that should be datetime fields (v1/v2 → v3 compatibility).

    Converts False values to None (clears the datetime field) and warns about True
    values that can't be automatically converted.

    Args:
        kwargs: Dictionary of keyword arguments to modify in-place
        field_mappings: Mapping of boolean field names to datetime field names
                       Example: {'sleep': 'sleep_at', 'expires': 'expires_at'}
        stacklevel: Stack level for warnings (default: 4)

    Example:
        >>> # Convert False to None
        >>> kwargs = {'name': 'Test', 'sleep': False, 'expires': False}
        >>> mappings = {'sleep': 'sleep_at', 'expires': 'expires_at'}
        >>> handle_boolean_datetime_fields(kwargs, mappings)
        >>> kwargs
        {'name': 'Test', 'sleep_at': None, 'expires_at': None}

        >>> # Warn about True (can't convert without datetime)
        >>> kwargs = {'sleep': True}
        >>> handle_boolean_datetime_fields(kwargs, mappings)
        # Raises DeprecationWarning about using datetime fields instead

        >>> # If both provided, datetime takes precedence
        >>> from datetime import datetime
        >>> kwargs = {'sleep': True, 'sleep_at': datetime(2025, 1, 1)}
        >>> handle_boolean_datetime_fields(kwargs, mappings)
        >>> kwargs
        {'sleep_at': datetime(2025, 1, 1)}  # boolean field ignored
    """
    converted_fields = []
    true_fields = []
    ignored_fields = []

    for bool_field, datetime_field in field_mappings.items():
        if bool_field in kwargs:
            value = kwargs.pop(bool_field)

            # If datetime field is already provided, prioritize it and ignore boolean
            if datetime_field in kwargs:
                ignored_fields.append(f'{bool_field} (using {datetime_field} instead)')
                continue

            if value is False:
                # Convert False to None (clear the datetime field)
                kwargs[datetime_field] = None
                converted_fields.append(
                    f'{bool_field} = False -> {datetime_field} = None'
                )
            elif value is True:
                # Can't convert True without a datetime value
                true_fields.append(bool_field)

    # Warn about fields ignored because datetime field was provided
    if ignored_fields:
        warnings.warn(
            f'Ignored boolean field(s): {", ".join(ignored_fields)}. '
            f'The datetime field takes precedence.',
            DeprecationWarning,
            stacklevel=stacklevel,
        )

    # Warn about fields that were automatically converted
    if converted_fields:
        warnings.warn(
            f'Automatically converted: {", ".join(converted_fields)}. '
            f'Consider using the datetime field equivalents directly.',
            DeprecationWarning,
            stacklevel=stacklevel,
        )

    # Warn about True values that couldn't be converted
    if true_fields:
        datetime_fields = [field_mappings[field] for field in true_fields]
        datetime_fields_str = ', '.join(f"'{field}'" for field in datetime_fields)
        warnings.warn(
            f'The {", ".join(true_fields)} boolean parameter(s) are not '
            f'supported in the current air-api version. Use '
            f'{datetime_fields_str} with datetime values instead.',
            DeprecationWarning,
            stacklevel=stacklevel,
        )
