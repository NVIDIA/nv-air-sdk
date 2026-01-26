# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Base backward compatibility mixin for common v1/v2 SDK patterns.
"""

from typing import Any

from air_sdk.bc.decorators import deprecated


class BaseCompatMixin:
    """Base mixin providing common v1/v2 SDK backward compatibility.

    This mixin provides methods that were common across multiple endpoints
    in v1/v2 SDK versions.
    """

    @deprecated(
        'full_update() is deprecated and may be removed in the future. '
        'Use update() instead.'
    )
    def full_update(self, *args: Any, **kwargs: Any) -> None:
        """Legacy full_update method from v1/v2. Maps to update().

        Note:
            This method is deprecated. Use update() instead.
            Maintained for backward compatibility with v1/v2 SDK.
        """
        super().update(*args, **kwargs)  # type: ignore[misc]


class BaseEndpointAPICompatMixin:
    """Mixin providing API-level backward compatibility for BaseEndpointAPI.

    This handles BC for API-level methods (create, list, etc.)
    where v1/v2 used different parameter or field names than v3.
    """

    @deprecated(
        'put() is deprecated and may be removed in the future. '
        'Use patch() for partial updates instead.'
    )
    def put(self, pk: Any, **kwargs: Any) -> Any:
        """
        PUT operation that delegates to PATCH since the API doesn't support true PUT.

        """
        return self.patch(pk, **kwargs)  # type: ignore[attr-defined]


class AirModelCompatMixin:
    """Mixin providing common v1/v2 SDK backward compatibility for AirModel.

    This mixin provides methods that were common across multiple endpoints
    in v1/v2 SDK versions.

    Subclasses can define the following class attributes to enable automatic
    field mapping and removal:
    - _FIELD_MAPPINGS: Dict[str, str] - Maps old field names to new ones
    - _REMOVED_FIELDS: List[str] - Fields that have been removed and should raise errors
    """

    def _check_and_map_field(self, name: str) -> str:
        """Check if field is removed or needs mapping, return mapped name.

        Args:
            name: The field name to check and potentially map

        Returns:
            The mapped field name (or original if no mapping needed)

        Raises:
            AttributeError: If the field has been removed
        """
        # Check for removed fields - raise AttributeError
        removed_fields = getattr(self.__class__, '_REMOVED_FIELDS', [])
        if name in removed_fields:
            raise AttributeError(
                f"The attribute '{name}' is no longer supported in the "
                f'current air-api version.'
            )

        # Field name mappings - warn and map to new name
        field_mappings = getattr(self.__class__, '_FIELD_MAPPINGS', {})
        if name in field_mappings:
            new_name: str = field_mappings[name]
            return new_name

        return name

    def __getattr__(self, name: str) -> Any:
        """Handle field name mappings and removed fields for reading.

        This method automatically:
        1. Checks if field was removed (raises AttributeError)
        2. Maps old field names to new ones (with deprecation warning)
        3. Calls super().__getattribute__() to complete the attribute access

        Subclasses define _REMOVED_FIELDS and _FIELD_MAPPINGS as class attributes.
        """
        name = self._check_and_map_field(name)
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Handle field name mappings and removed fields for writing.

        This method automatically:
        1. Checks if field was removed (raises AttributeError)
        2. Maps old field names to new ones (with deprecation warning)
        3. Calls super().__setattr__() to complete the attribute assignment

        Subclasses define _REMOVED_FIELDS and _FIELD_MAPPINGS as class attributes.
        """
        name = self._check_and_map_field(name)
        super().__setattr__(name, value)
