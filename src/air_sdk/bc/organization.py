# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Organization-specific backward compatibility for v1/v2 SDK.
"""

from __future__ import annotations

from typing import Any, Iterator

from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.bc.utils import drop_removed_fields, map_field_names


class OrganizationCompatMixin(AirModelCompatMixin):
    """Mixin providing Organization-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with organization fields from older SDK versions.

    Field mappings (v1/v2 → v3):
    - name → org_display_name
    - storage → disk_storage_total

    Removed fields:
    - member_count: No longer available in the new API
    - resource_budget: Now embedded in Organization model (not a FK)
    - list_members(): Organization members endpoint no longer exists
    - cpu_used, memory_used, storage_used, etc.: Now in usage dict
    """

    # Field mappings: old (v1/v2) → new (v3)
    _FIELD_MAPPINGS = {
        'name': 'org_display_name',
        'storage': 'disk_storage_total',
    }

    # Fields that were removed in v3
    _REMOVED_FIELDS = [
        'member_count',
        'resource_budget',
        'cpu_used',
        'memory_used',
        'storage_used',
        'simulations',
        'simulations_used',
        'image_uploads',
        'image_uploads_used',
        'userconfigs_used',
    ]


class OrganizationEndpointAPICompatMixin:
    """Mixin providing API-level backward compatibility for Organization endpoints.

    This handles BC for API-level methods (list) where v1/v2 used different
    parameter or field names than v3.
    """

    def list(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        """List method with v1/v2 field name compatibility for Organizations.

        Handles:
        - Field name mapping for filters (see OrganizationCompatMixin._FIELD_MAPPINGS)
        - Removed filters (see OrganizationCompatMixin._REMOVED_FIELDS)
        """
        # Drop removed fields (includes both body fields and filters)
        drop_removed_fields(kwargs, OrganizationCompatMixin._REMOVED_FIELDS)
        # Map old field names to new ones for filtering
        map_field_names(kwargs, OrganizationCompatMixin._FIELD_MAPPINGS)

        return super().list(*args, **kwargs)  # type: ignore[no-any-return,misc]
