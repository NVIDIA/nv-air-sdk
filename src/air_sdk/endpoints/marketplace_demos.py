# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import Any

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc import (
    BaseCompatMixin,
    BaseEndpointAPICompatMixin,
    MarketplaceDemoCompatMixin,
    MarketplaceDemoEndpointAPICompatMixin,
)
from air_sdk.endpoints import mixins

# Import Simulation at runtime (not just TYPE_CHECKING) because get_type_hints() needs it
from air_sdk.endpoints.simulations import Simulation
from air_sdk.utils import join_urls, raise_if_invalid_response, validate_payload_types


@dataclass(eq=False)
class MarketplaceDemo(BaseCompatMixin, MarketplaceDemoCompatMixin, AirModel):
    id: str
    name: str
    demo: Simulation = field(metadata=AirModel.FIELD_FOREIGN_KEY)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    creator: str = field(repr=False)
    documentation: str | None = field(repr=False)
    tags: list[str] = field(repr=False)
    like_count: int = field(repr=False)
    liked_by_client: bool = field(repr=False)
    published: bool = field(repr=False)
    description: str | None
    repo: str | None
    icon: str | None

    @classmethod
    def get_model_api(cls) -> type[MarketplaceDemoEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return MarketplaceDemoEndpointAPI

    @property
    def model_api(self) -> MarketplaceDemoEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    def publish(self, **kwargs: Any) -> None:
        self.model_api.publish(marketplace_demo=self, **kwargs)

    def unpublish(self, **kwargs: Any) -> None:
        self.model_api.unpublish(marketplace_demo=self, **kwargs)

    def provision(self, **kwargs: Any) -> Simulation:
        return self.model_api.provision(marketplace_demo=self, **kwargs)


class MarketplaceDemoEndpointAPI(
    MarketplaceDemoEndpointAPICompatMixin,
    BaseEndpointAPICompatMixin,
    mixins.ListApiMixin[MarketplaceDemo],
    mixins.CreateApiMixin[MarketplaceDemo],
    mixins.GetApiMixin[MarketplaceDemo],
    mixins.PatchApiMixin[MarketplaceDemo],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[MarketplaceDemo],
):
    API_PATH = 'marketplace/demos'
    API_PUBLISH_PATH = 'publish'
    API_UNPUBLISH_PATH = 'unpublish'
    API_PROVISION_PATH = 'provision'
    model = MarketplaceDemo

    @validate_payload_types
    def publish(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> None:
        marketplace_demo_id = (
            marketplace_demo.id
            if isinstance(marketplace_demo, MarketplaceDemo)
            else marketplace_demo
        )

        url = join_urls(self.url, str(marketplace_demo_id), self.API_PUBLISH_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))

        raise_if_invalid_response(
            response, status_code=HTTPStatus.NO_CONTENT, data_type=None
        )

        if isinstance(marketplace_demo, MarketplaceDemo):
            marketplace_demo.refresh()

    @validate_payload_types
    def unpublish(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> None:
        marketplace_demo_id = (
            marketplace_demo.id
            if isinstance(marketplace_demo, MarketplaceDemo)
            else marketplace_demo
        )

        url = join_urls(self.url, str(marketplace_demo_id), self.API_UNPUBLISH_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))

        raise_if_invalid_response(
            response, status_code=HTTPStatus.NO_CONTENT, data_type=None
        )

        if isinstance(marketplace_demo, MarketplaceDemo):
            marketplace_demo.refresh()

    @validate_payload_types
    def provision(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> Simulation:
        marketplace_demo_id = (
            marketplace_demo.id
            if isinstance(marketplace_demo, MarketplaceDemo)
            else marketplace_demo
        )

        url = join_urls(self.url, str(marketplace_demo_id), self.API_PROVISION_PATH)
        response = self.__api__.client.post(url, data=mixins.serialize_payload(kwargs))

        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)

        if isinstance(marketplace_demo, MarketplaceDemo):
            marketplace_demo.refresh()

        # The API returns a Simulation object
        return self.__api__.simulations.load_model(response.json())
