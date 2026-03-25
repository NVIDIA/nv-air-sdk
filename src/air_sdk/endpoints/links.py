# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TypedDict

from air_sdk.air_model import (
    AirModel,
    BaseEndpointAPI,
    DataDict,
)
from air_sdk.bc import (
    BaseCompatMixin,
    LinkCompatMixin,
    LinkEndpointAPICompatMixin,
)
from air_sdk.endpoints import mixins
from air_sdk.endpoints.interfaces import Interface


class LinksLabels(TypedDict):
    """Properties/labels of a link."""

    cable_length: str  # NotRequired[str] (Python 3.11+)


@dataclass(eq=False)
class Link(BaseCompatMixin, LinkCompatMixin, AirModel):
    id: str
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    interfaces: list[Interface] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    labels: LinksLabels | None = field(default=None, repr=False)

    @classmethod
    def get_model_api(cls) -> type[LinkEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return LinkEndpointAPI

    @property
    def model_api(self) -> LinkEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)


class LinkEndpointAPI(
    LinkEndpointAPICompatMixin,
    mixins.ListApiMixin[Link],
    mixins.CreateApiMixin[Link],
    mixins.GetApiMixin[Link],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Link],
):
    API_PATH = 'simulations/nodes/interfaces/links/'
    model = Link

    def load_model(self, data: DataDict) -> Link:
        """Load a Link model, transforming interfaces to foreign key format.

        The API returns interfaces as a list of objects with id, name, and node_name.
        We transform this to a list of IDs so the SDK can load them as foreign keys.

        Args:
            data: Raw API response data

        Returns:
            Link model instance with interfaces as foreign keys
        """
        # Transform interfaces from [{"id": "...","name": "...","node_name": "..."}, ...]
        # to ["uuid1", "uuid2", ...] for foreign key loading
        if 'interfaces' in data and isinstance(data['interfaces'], list):
            resolved: list[object] = []
            for intf in data['interfaces']:
                if isinstance(intf, dict):
                    intf_id = intf.get('id')
                    if intf_id is None:
                        link_id = data.get('id', '<unknown>')
                        raise ValueError(
                            f"Interface dict missing 'id' key in link {link_id}: {intf}"
                        )
                    resolved.append(intf_id)
                else:
                    resolved.append(intf)
            data['interfaces'] = resolved

        # Call parent load_model with transformed data
        return super().load_model(data)
