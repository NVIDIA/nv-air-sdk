# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
UserConfig-specific backward compatibility for v1/v2 SDK.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from air_sdk.bc.base import BaseEndpointAPICompatMixin
from air_sdk.bc.utils import drop_removed_fields

if TYPE_CHECKING:
    from air_sdk.endpoints.user_configs import UserConfig

# Fields that were removed in v3 (were in v2 API but not in v3)
# TODO: Remove organization_budget and organization(?) once
# ResourceBudget endpoint is implemented in v3:
_USER_CONFIG_REMOVED_FIELDS = [
    'organization',
    'organization_budget',
    'owner',
    'owner_budget',
]


class UserConfigEndpointAPICompatMixin(BaseEndpointAPICompatMixin):
    """Mixin providing UserConfigEndpointAPI v1/v2 SDK backward compatibility.

    This maintains compatibility with endpoint API methods from older SDK versions.

    Handles:
    - Removed parameters in create(): organization, organization_budget,
      owner, owner_budget (v3 API auto-assigns these)
    """

    def create(self, *args: Any, **kwargs: Any) -> UserConfig:
        """Create a user config with v1/v2 parameter compatibility.

        Drops parameters that were removed in v3:
        - organization, organization_budget
        - owner, owner_budget

        In v3, user configs are automatically associated with the user's
        default organization and owner.
        """
        # Drop removed fields and warn user
        drop_removed_fields(kwargs, _USER_CONFIG_REMOVED_FIELDS)

        # Call parent create
        return super().create(*args, **kwargs)  # type: ignore[misc, no-any-return]

    def patch(self, *args: Any, **kwargs: Any) -> UserConfig:
        """Patch a user config with v1/v2 parameter compatibility.

        Drops parameters that were removed in v3:
        - organization, organization_budget
        - owner, owner_budget
        """
        drop_removed_fields(kwargs, _USER_CONFIG_REMOVED_FIELDS)
        return super().patch(*args, **kwargs)  # type: ignore[misc, no-any-return]

    def put(self, *args: Any, **kwargs: Any) -> UserConfig:
        """Put a user config with v1/v2 parameter compatibility.

        Drops parameters that were removed in v3:
        - organization, organization_budget
        - owner, owner_budget
        """
        drop_removed_fields(kwargs, _USER_CONFIG_REMOVED_FIELDS)
        return super().put(*args, **kwargs)  # type: ignore[no-any-return]
