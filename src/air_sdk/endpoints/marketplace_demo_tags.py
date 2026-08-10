# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from air_sdk.air_model import AirModel, BaseEndpointAPI
from air_sdk.endpoints import mixins

if TYPE_CHECKING:
    from air_sdk.endpoints.marketplace_demos import MarketplaceDemoEndpointAPI


@dataclass(eq=False)
class MarketplaceDemoTag(AirModel):
    """A tag associated with a marketplace demo."""

    id: str
    name: str
    is_public: bool = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type[MarketplaceDemoTagEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return MarketplaceDemoTagEndpointAPI

    @property
    def model_api(self) -> MarketplaceDemoTagEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    @property
    def marketplace_demos(self) -> MarketplaceDemoEndpointAPI:
        """Marketplace demos assigned this tag."""
        from air_sdk.endpoints.marketplace_demos import MarketplaceDemoEndpointAPI

        return MarketplaceDemoEndpointAPI(
            self.__api__, default_filters={'tags': self.name}
        )


class MarketplaceDemoTagEndpointAPI(
    mixins.ListApiMixin[MarketplaceDemoTag],
    mixins.GetApiMixin[MarketplaceDemoTag],
    mixins.PatchApiMixin[MarketplaceDemoTag],
    mixins.CreateApiMixin[MarketplaceDemoTag],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[MarketplaceDemoTag],
):
    """Endpoint API for marketplace demo tags."""

    API_PATH = 'marketplace/demos/tags'
    model = MarketplaceDemoTag
