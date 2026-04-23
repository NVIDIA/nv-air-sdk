# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from air_sdk.endpoints.links import LinkEndpointAPI
    from air_sdk.endpoints.services import ServiceEndpointAPI

from air_sdk.air_model import (
    AirModel,
    BaseEndpointAPI,
    PrimaryKey,
)
from air_sdk.bc import (
    BaseCompatMixin,
    InterfaceCompatMixin,
    InterfaceEndpointAPICompatMixin,
)
from air_sdk.endpoints import mixins
from air_sdk.endpoints.nodes import Node
from air_sdk.utils import raise_if_invalid_response, validate_payload_types


@dataclass
class InterfaceLabels:
    interface_role: str | None
    scalable_unit: int | None


@dataclass(eq=False)
class Interface(BaseCompatMixin, InterfaceCompatMixin, AirModel):
    id: str
    name: str
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    node: Node = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    interface_type: str  # One of: DATA_PLANE_INTF, PCIE_INTF, OOB_INTF
    mac_address: str
    connection: Interface | None = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    outbound: bool
    labels: InterfaceLabels | None = field(repr=False)
    interface_role: str | None = field(default=None, repr=False)
    scalable_unit: int | None = field(default=None, repr=False)

    @classmethod
    def get_model_api(cls) -> type[InterfaceEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return InterfaceEndpointAPI

    @property
    def model_api(self) -> InterfaceEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    @property
    def links(self) -> LinkEndpointAPI:
        from air_sdk.endpoints.links import LinkEndpointAPI

        return LinkEndpointAPI(
            self.__api__, default_filters={'interface': str(self.__pk__)}
        )

    def breakout(self, **kwargs: Any) -> list[Interface]:
        return self.model_api.breakout(interface=self, **kwargs)

    def revert_breakout(self, **kwargs: Any) -> Interface:
        return self.model_api.revert_breakout(interface=self, **kwargs)

    @property
    def services(self) -> ServiceEndpointAPI:
        from air_sdk.endpoints.services import ServiceEndpointAPI

        return ServiceEndpointAPI(
            self.__api__, default_filters={'interface': str(self.__pk__)}
        )


class InterfaceEndpointAPI(
    InterfaceEndpointAPICompatMixin,
    mixins.ListApiMixin[Interface],
    mixins.CreateApiMixin[Interface],
    mixins.GetApiMixin[Interface],
    mixins.PatchApiMixin[Interface],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Interface],
):
    API_PATH = 'simulations/nodes/interfaces/'
    BREAKOUT_PATH = 'breakout'
    REVERT_BREAKOUT_PATH = 'revert-breakout'
    model = Interface

    @validate_payload_types
    def breakout(
        self, *, interface: Interface | PrimaryKey, **kwargs: Any
    ) -> list[Interface]:
        url = mixins.build_resource_url(self.url, interface, self.BREAKOUT_PATH)
        response = self.__api__.client.post(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(response, status_code=HTTPStatus.OK, data_type=list)

        if isinstance(interface, Interface):
            interface.refresh()

        return [self.load_model(data) for data in response.json()]

    @validate_payload_types
    def revert_breakout(
        self, *, interface: Interface | PrimaryKey, **kwargs: Any
    ) -> Interface:
        url = mixins.build_resource_url(self.url, interface, self.REVERT_BREAKOUT_PATH)
        response = self.__api__.client.post(
            url, data=mixins.serialize_payload(kwargs) if kwargs else None
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)

        if isinstance(interface, Interface):
            interface.refresh()

        return self.load_model(response.json())
