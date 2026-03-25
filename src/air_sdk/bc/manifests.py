# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Manifest-specific backward compatibility for v2 SDK.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Iterator, Type

from air_sdk.air_model import PrimaryKey
from air_sdk.bc.base import AirModelCompatMixin, BaseEndpointAPICompatMixin
from air_sdk.bc.utils import drop_removed_fields, map_field_names

if TYPE_CHECKING:
    from air_sdk.endpoints.manifests import Manifest


class ManifestCompatMixin(AirModelCompatMixin):
    """Mixin providing Manifest-specific v2 SDK backward compatibility.

    This maintains compatibility with manifest fields and methods from older
    SDK versions:
    - Field mappings: organization → org_name (v2 → v3)
    - Removed fields: owner (completely removed)
    - Read-only fields: org_name (set by API from NGC)

    Note:
        'organization' is in _FIELD_MAPPINGS for backwards compatibility when
        reading (my_manifest.organization) and when writing: if the user passes
        organization, we map it to org_name then drop org_name (read-only).
        So create/update/patch: map_field_names first (organization → org_name,
        warn), then drop_removed_fields so org_name is dropped and a second
        warning is emitted (read-only). Passing org_name directly is also
        dropped and warned via _READ_ONLY_FIELDS.
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

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update method with v2 field name compatibility for Manifests.

        Normalizes old (v2) field names to v3 equivalents
        (see _FIELD_MAPPINGS).

        Drops unsupported fields in _REMOVED_FIELDS and model _READ_ONLY_FIELDS.

        Note:
            This method overrides the parent update() to provide field mapping.
        """
        map_field_names(kwargs, ManifestCompatMixin._FIELD_MAPPINGS)
        drop_removed_fields(kwargs, self._REMOVED_FIELDS + self._READ_ONLY_FIELDS)

        # Call the parent update() method
        super().update(*args, **kwargs)  # type: ignore[misc]


class ManifestEndpointAPICompatMixin(BaseEndpointAPICompatMixin):
    """Mixin providing API-level backward compatibility for Manifest endpoints.

    This handles BC for API-level methods (create, list, patch)
    where v2 used different parameter or field names than v3.
    """

    # Provided by BaseEndpointAPI when mixed in (e.g. ManifestEndpointAPI.model)
    model: ClassVar[Type[Any]]

    def create(self, *args: Any, **kwargs: Any) -> Manifest:
        """Create method with v2 field name compatibility for Manifests.

        Handles:
        - Field name mapping (see ManifestCompatMixin._FIELD_MAPPINGS)
        - Removed fields (see ManifestCompatMixin._REMOVED_FIELDS)
        - Read-only fields (see Manifest._READ_ONLY_FIELDS)
        """
        map_field_names(kwargs, ManifestCompatMixin._FIELD_MAPPINGS)
        drop_removed_fields(
            kwargs,
            ManifestCompatMixin._REMOVED_FIELDS + self.model._READ_ONLY_FIELDS,
        )

        # Call the parent create() method
        return super().create(*args, **kwargs)  # type: ignore[no-any-return,misc]

    def list(self, *args: Any, **kwargs: Any) -> Iterator[Manifest]:
        """List method with v2 field name compatibility for Manifests.

        Handles:
        - Field name mapping for filters (see ManifestCompatMixin._FIELD_MAPPINGS)
        - Removed filters (see ManifestCompatMixin._REMOVED_FIELDS)
        - Read-only filters (see Manifest._READ_ONLY_FIELDS)
        """
        map_field_names(kwargs, ManifestCompatMixin._FIELD_MAPPINGS)
        drop_removed_fields(
            kwargs,
            ManifestCompatMixin._REMOVED_FIELDS + self.model._READ_ONLY_FIELDS,
        )

        return super().list(*args, **kwargs)  # type: ignore[no-any-return,misc]

    def patch(self, pk: PrimaryKey, **kwargs: Any) -> Manifest:
        """Patch method with v2 field name compatibility for Manifests.

        Handles:
        - Field name mapping (see ManifestCompatMixin._FIELD_MAPPINGS)
        - Removed fields (see ManifestCompatMixin._REMOVED_FIELDS)
        - Read-only fields (see Manifest._READ_ONLY_FIELDS)
        """
        # Map v2 names first, then drop removed/read-only
        map_field_names(kwargs, ManifestCompatMixin._FIELD_MAPPINGS)
        drop_removed_fields(
            kwargs,
            ManifestCompatMixin._REMOVED_FIELDS + self.model._READ_ONLY_FIELDS,
        )

        return super().patch(pk, **kwargs)  # type: ignore[no-any-return,misc]
