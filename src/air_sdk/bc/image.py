# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Image-specific backward compatibility for v1/v2 SDK.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.bc.utils import drop_removed_fields, map_field_names

if TYPE_CHECKING:
    from air_sdk.endpoints.images import Image


class ImageCompatMixin(AirModelCompatMixin):
    """Mixin providing Image-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with image fields and methods from older
    SDK versions:
    - Field mappings: agent_enabled → includes_air_agent,
      filename → filepath, local_file_path → filepath (v1/v2 → v3)
    """

    # Field mappings: old (v1/v2) → new (v3)
    _FIELD_MAPPINGS = {
        'agent_enabled': 'includes_air_agent',
        'filename': 'filepath',
        'local_file_path': 'filepath',
    }

    # Fields and filters that were removed in v3
    _REMOVED_FIELDS = [
        'archived',
        'bios',
        'bus',
        'console_support',
        'features',
        'organization',
        'simx',
        'uploader',
        'can_edit',
        'organization_name',
        'uploader_username',
        'contact',
    ]

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update method with v1/v2 field name compatibility for Images.

        Normalizes old (v1/v2) field names to v3 equivalents
        (see _FIELD_MAPPINGS).

        Drops unsupported fields in _REMOVED_FIELDS.

        Note:
            This method overrides the parent update() to provide field mapping.
        """
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(kwargs, self._REMOVED_FIELDS)
        map_field_names(kwargs, self._FIELD_MAPPINGS)

        # Call the parent update() method
        super().update(*args, **kwargs)  # type: ignore[misc]

    def upload(self, *args: Any, **kwargs: Any) -> Image:
        """Upload method with v1/v2 field name compatibility for Images."""
        # Field mapping and cleanup happens in ImageEndpointAPICompatMixin.upload()
        return self.model_api.upload(image=self, *args, **kwargs)  # type: ignore[no-any-return]

    def publish(self, *args: Any, **kwargs: Any) -> Image:
        """Publish method with v1/v2 field name compatibility for Images."""
        # Clean up happens in ImageEndpointAPICompatMixin.publish()
        return self.model_api.publish(image=self, *args, **kwargs)  # type: ignore[no-any-return]


class ImageEndpointAPICompatMixin:
    """Mixin providing API-level backward compatibility for Image endpoints.

    This handles BC for API-level methods (create, list, upload, publish)
    where v1/v2 used different parameter or field names than v3.
    """

    def create(self, *args: Any, **kwargs: Any) -> Image:
        """Create method with v1/v2 field name compatibility for Images.

        Handles:
        - Field name mapping (see ImageCompatMixin._FIELD_MAPPINGS)
        - Removed fields (see ImageCompatMixin._REMOVED_FIELDS)
        """
        # Clean up kwargs for v3 (do this once at the start)
        drop_removed_fields(kwargs, ImageCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, ImageCompatMixin._FIELD_MAPPINGS)

        # Call the v3 create() method
        return self.create_v3(*args, **kwargs)  # type: ignore[attr-defined, no-any-return]

    def list(self, *args: Any, **kwargs: Any) -> Iterator[Image]:
        """List method with v1/v2 field name compatibility for Images.

        Handles:
        - Field name mapping (see ImageCompatMixin._FIELD_MAPPINGS)
        - Removed filters (see ImageCompatMixin._REMOVED_FIELDS)
        """
        # Drop removed fields (includes both body fields and filters)
        drop_removed_fields(kwargs, ImageCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, ImageCompatMixin._FIELD_MAPPINGS)

        return super().list(*args, **kwargs)  # type: ignore[no-any-return,misc]

    def patch(self, *args: Any, **kwargs: Any) -> Image:
        """Patch method with v1/v2 field name compatibility for Images.

        Handles:
        - Field name mapping (see ImageCompatMixin._FIELD_MAPPINGS)
        - Removed fields (see ImageCompatMixin._REMOVED_FIELDS)
        """
        drop_removed_fields(kwargs, ImageCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, ImageCompatMixin._FIELD_MAPPINGS)
        return super().patch(*args, **kwargs)  # type: ignore[no-any-return,misc]

    def upload(self, *args: Any, **kwargs: Any) -> Image:
        """Upload method with v1/v2 field name compatibility for Images.

        Handles:
        - Field name mapping (see ImageCompatMixin._FIELD_MAPPINGS)
        - Removed fields (see ImageCompatMixin._REMOVED_FIELDS)
        """
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(kwargs, ImageCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, ImageCompatMixin._FIELD_MAPPINGS)

        return self.upload_v3(*args, **kwargs)  # type: ignore[attr-defined, no-any-return]

    def publish(self, *args: Any, **kwargs: Any) -> Image:
        """Publish method with v1/v2 field name compatibility for Images.

        Handles:
        - Removed fields (see ImageCompatMixin._REMOVED_FIELDS)
        """
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(kwargs, ImageCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, ImageCompatMixin._FIELD_MAPPINGS)

        # Call the parent publish() method
        return self.publish_v3(*args, **kwargs)  # type: ignore[attr-defined, no-any-return]
