# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Manifest-specific backward compatibility for v2 SDK.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

from air_sdk.air_model import PrimaryKey
from air_sdk.bc.base import AirModelCompatMixin, BaseEndpointAPICompatMixin
from air_sdk.bc.utils import drop_removed_fields, map_field_names

if TYPE_CHECKING:
    from air_sdk.endpoints.manifests import Manifest


class ManifestCompatMixin(AirModelCompatMixin):
    """Mixin providing Manifest-specific v2 SDK backward compatibility.

    This maintains compatibility with manifest fields and methods from older
    SDK versions:
    - Field mappings: organization → org_name (v2 → v3, read-only)
    - Removed fields: owner (completely removed)
    - Read-only fields: organization (readable but not writable)

    Note:
        'organization' is in _FIELD_MAPPINGS for backwards compatibility when
        reading (my_manifest.organization), but it's also in _READ_ONLY_FIELDS
        so it gets dropped during create/update/patch operations since v3 takes
        org_name from NGC.

    Removed fields and field mappings are automatically handled by AirModelCompatMixin.
    """

    # Field mappings: old (v2) → new (v3)
    # organization is read-only mapping - dropped on input (see below)
    _FIELD_MAPPINGS = {
        'organization': 'org_name',
    }

    # Fields that were removed in v3
    _REMOVED_FIELDS = [
        'owner',
    ]

    # Fields that are read-only (accessible via _FIELD_MAPPINGS but dropped on input)
    _READ_ONLY_FIELDS = [
        'organization',
    ]

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update method with v2 field name compatibility for Manifests.

        Normalizes old (v2) field names to v3 equivalents
        (see _FIELD_MAPPINGS).

        Drops unsupported fields in _REMOVED_FIELDS and _READ_ONLY_FIELDS.

        Note:
            This method overrides the parent update() to provide field mapping.
        """
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(kwargs, self._REMOVED_FIELDS + self._READ_ONLY_FIELDS)
        map_field_names(kwargs, self._FIELD_MAPPINGS)

        # Call the parent update() method
        super().update(*args, **kwargs)  # type: ignore[misc]


class ManifestEndpointAPICompatMixin(BaseEndpointAPICompatMixin):
    """Mixin providing API-level backward compatibility for Manifest endpoints.

    This handles BC for API-level methods (create, list, patch)
    where v2 used different parameter or field names than v3.
    """

    def create(self, *args: Any, **kwargs: Any) -> Manifest:
        """Create method with v2 field name compatibility for Manifests.

        Handles:
        - Field name mapping (see ManifestCompatMixin._FIELD_MAPPINGS)
        - Removed fields (see ManifestCompatMixin._REMOVED_FIELDS)
        - Read-only fields (see ManifestCompatMixin._READ_ONLY_FIELDS)
        """
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(
            kwargs,
            ManifestCompatMixin._REMOVED_FIELDS + ManifestCompatMixin._READ_ONLY_FIELDS,
        )
        map_field_names(kwargs, ManifestCompatMixin._FIELD_MAPPINGS)

        # Call the parent create() method
        return super().create(*args, **kwargs)  # type: ignore[no-any-return,misc]

    def list(self, *args: Any, **kwargs: Any) -> Iterator[Manifest]:
        """List method with v2 field name compatibility for Manifests.

        Handles:
        - Field name mapping for filters (see ManifestCompatMixin._FIELD_MAPPINGS)
        - Removed filters (see ManifestCompatMixin._REMOVED_FIELDS)
        - Read-only filters (see ManifestCompatMixin._READ_ONLY_FIELDS)
        """
        # Drop removed fields (includes both body fields and filters)
        drop_removed_fields(
            kwargs,
            ManifestCompatMixin._REMOVED_FIELDS + ManifestCompatMixin._READ_ONLY_FIELDS,
        )
        map_field_names(kwargs, ManifestCompatMixin._FIELD_MAPPINGS)

        return super().list(*args, **kwargs)  # type: ignore[no-any-return,misc]

    def patch(self, pk: PrimaryKey, **kwargs: Any) -> Manifest:
        """Patch method with v2 field name compatibility for Manifests.

        Handles:
        - Field name mapping (see ManifestCompatMixin._FIELD_MAPPINGS)
        - Removed fields (see ManifestCompatMixin._REMOVED_FIELDS)
        - Read-only fields (see ManifestCompatMixin._READ_ONLY_FIELDS)
        """
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(
            kwargs,
            ManifestCompatMixin._REMOVED_FIELDS + ManifestCompatMixin._READ_ONLY_FIELDS,
        )
        map_field_names(kwargs, ManifestCompatMixin._FIELD_MAPPINGS)

        return super().patch(pk, **kwargs)  # type: ignore[no-any-return,misc]
