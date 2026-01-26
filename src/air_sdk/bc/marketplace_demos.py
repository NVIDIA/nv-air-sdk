# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
MarketplaceDemo-specific backward compatibility for v1/v2 SDK.
"""

from __future__ import annotations

from typing import Any

from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.bc.utils import map_field_names


class MarketplaceDemoCompatMixin(AirModelCompatMixin):
    """Mixin providing MarketplaceDemo-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with MarketplaceDemo fields and methods from older
    SDK versions:
    - Field mappings: liked_by_account → liked_by_client, owner/owner_email → creator,
      snapshot → demo (v1/v2 → v3)
    """

    # Field mappings: old (v1/v2) → new (v3)
    _FIELD_MAPPINGS = {
        'liked_by_account': 'liked_by_client',
        'owner_email': 'creator',
        'snapshot': 'demo',
        'owner': 'creator',
    }

    # Fields and filters that were removed in v3
    _REMOVED_FIELDS: list[str] = []

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update method with field name compatibility for MarketplaceDemos.

        Normalizes old (v1/v2) field names to v3 equivalents
        (see _FIELD_MAPPINGS).

        Note:
            Fields like owner/creator, snapshot/demo, and published are read-only in v3.
            This method overrides the parent update() to provide field mapping.
        """
        # Map remaining v1/v2 field names to v3 equivalents
        map_field_names(kwargs, self._FIELD_MAPPINGS)
        super().update(*args, **kwargs)  # type: ignore[misc]
        return self  # type: ignore[return-value]


class MarketplaceDemoEndpointAPICompatMixin:
    """Mixin providing API-level backward compatibility for MarketplaceDemo endpoints.

    This handles BC for API-level methods (create, list, etc.)
    where v1/v2 used different parameter or field names than v3.
    """

    def list(self, *args: Any, **kwargs: Any) -> Any:
        """List marketplace demos with v1/v2 filter name compatibility."""
        map_field_names(kwargs, MarketplaceDemoCompatMixin._FIELD_MAPPINGS)
        return super().list(*args, **kwargs)  # type: ignore[misc]

    def create(self, *args: Any, **kwargs: Any) -> Any:
        """Create a marketplace demo with v1/v2 field name compatibility.

        Normalizes old (v1/v2) field names to v3 equivalents:
        - snapshot → simulation

        Fields that are not creatable in v3:
        - owner / creator (auto-populated by API)
        - published (auto-populated by API)

        """
        # Handle 'snapshot' -> 'simulation' mapping BEFORE general field mapping
        # In v1/v2, 'snapshot' was used; in v3 it's 'simulation'
        if 'snapshot' in kwargs:
            kwargs['simulation'] = kwargs.pop('snapshot')

        return super().create(*args, **kwargs)  # type: ignore[misc]
