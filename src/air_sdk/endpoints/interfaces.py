# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
from air_sdk.utils import join_urls, raise_if_invalid_response, validate_payload_types


@dataclass
class InterfaceAttributes:
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
    attributes: InterfaceAttributes | None = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type[InterfaceEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return InterfaceEndpointAPI

    @property
    def model_api(self) -> InterfaceEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    @validate_payload_types
    def connect(self, *, target: Interface | PrimaryKey) -> Interface:
        return self.model_api.connect(interface=self, target=target)

    def disconnect(self) -> Interface:
        return self.model_api.disconnect(interface=self)

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
    SET_CONNECTION_PATH = 'set-connection'
    model = Interface

    def set_connection(
        self,
        interface: Interface | PrimaryKey,
        target: Interface | PrimaryKey | None,
    ) -> Interface:
        """Helper method to set or clear interface connection.

        Args:
            interface: The interface to modify
            target: The target interface to connect to, or None to disconnect

        Returns:
            The updated interface
        """
        interface_id = interface.id if isinstance(interface, Interface) else interface
        url = join_urls(self.url, str(interface_id), self.SET_CONNECTION_PATH)
        response = self.__api__.client.patch(
            url, data=mixins.serialize_payload({'target': target})
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        if isinstance(interface, Interface):
            interface.refresh()
        if isinstance(target, Interface):
            target.refresh()
        return self.load_model(response.json())

    @validate_payload_types
    def connect(
        self, *, interface: Interface | PrimaryKey, target: Interface | PrimaryKey
    ) -> Interface:
        return self.set_connection(interface, target)

    @validate_payload_types
    def disconnect(self, *, interface: Interface | PrimaryKey) -> Interface:
        return self.set_connection(interface, None)
