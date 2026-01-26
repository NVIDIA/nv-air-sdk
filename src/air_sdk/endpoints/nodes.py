# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc import (
    BaseCompatMixin,
    NodeCompatMixin,
    NodeEndpointAPICompatMixin,
)
from air_sdk.endpoints import mixins
from air_sdk.endpoints.images import Image
from air_sdk.endpoints.simulations import Simulation
from air_sdk.endpoints.systems import System
from air_sdk.utils import join_urls, raise_if_invalid_response, validate_payload_types

if TYPE_CHECKING:
    from air_sdk.endpoints.interfaces import InterfaceEndpointAPI
    from air_sdk.endpoints.services import Service, ServiceEndpointAPI


@dataclass(eq=False)
class Node(BaseCompatMixin, NodeCompatMixin, AirModel):
    id: str
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    name: str
    simulation: Simulation = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    image: Image = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    category: str = field(repr=False)
    state: str
    status_from_worker: str = field(repr=False)
    split_options: list[int] | None = field(repr=False)
    cpu: int = field(repr=False)
    memory: int = field(repr=False)
    storage: int = field(repr=False)
    pos_x: int = field(repr=False)
    pos_y: int = field(repr=False)
    cdrom: dict[str, Any] | None = field(repr=False)
    storage_pci: dict[str, Any] | None = field(repr=False)
    attributes: dict[str, Any] | None = field(repr=False)
    advanced: dict[str, Any] = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type[NodeEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model."""
        return NodeEndpointAPI

    @property
    def model_api(self) -> NodeEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    def delete_all_node_instructions(self) -> None:
        """Delete all node instructions for this node."""
        for instruction in self.instructions.list():
            instruction.delete()

    def reset(self, **kwargs: Any) -> None:
        self.model_api.reset(node=self, **kwargs)

    def rebuild(self, **kwargs: Any) -> None:
        self.model_api.rebuild(node=self, **kwargs)

    @property
    def instructions(self) -> Any:
        from air_sdk.endpoints.node_instructions import NodeInstructionEndpointAPI

        return NodeInstructionEndpointAPI(
            self.__api__, default_filters={'node': str(self.__pk__)}
        )

    @property
    def services(self) -> ServiceEndpointAPI:
        from air_sdk.endpoints.services import ServiceEndpointAPI

        return ServiceEndpointAPI(
            self.__api__, default_filters={'node': str(self.__pk__)}
        )

    @validate_payload_types
    def create_service(self, *, interface_name: str, **kwargs: Any) -> Service:
        # Resolve interface name to interface ID
        interface_obj = next(
            self.__api__.interfaces.list(node=self.id, name=interface_name), None
        )
        if not interface_obj:
            raise ValueError(
                f'Interface "{interface_name}" not found on node "{self.name}"'
            )
        interface_id = str(interface_obj.id)

        return self.services.create(interface=interface_id, **kwargs)

    @property
    def interfaces(self) -> InterfaceEndpointAPI:
        from air_sdk.endpoints.interfaces import InterfaceEndpointAPI

        return InterfaceEndpointAPI(
            self.__api__, default_filters={'node': str(self.__pk__)}
        )


class NodeEndpointAPI(
    NodeEndpointAPICompatMixin,
    mixins.ListApiMixin[Node],
    mixins.CreateApiMixin[Node],
    mixins.GetApiMixin[Node],
    mixins.PatchApiMixin[Node],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Node],
):
    API_PATH = 'simulations/nodes/'
    sim_path = 'simulations/'
    from_system_node_path = 'from-system-node/'
    model = Node

    @validate_payload_types
    def update(self, *, node: Node | PrimaryKey, **kwargs: Any) -> Node:
        node_id = node.id if isinstance(node, Node) else node
        return self.patch(node_id, **kwargs)

    @validate_payload_types
    def create_from_system_node(self, **kwargs: Any) -> Node:
        url = join_urls(self.url, self.from_system_node_path)
        response = self.__api__.client.post(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        return self.load_model(response.json())

    def list_system_nodes(self, **kwargs: Any) -> Iterator[System]:
        return self.__api__.systems.list(**kwargs)

    def reset(self, *, node: Node | PrimaryKey, **kwargs: Any) -> None:
        if isinstance(node, Node):
            resolved_node = node
        else:
            resolved_node = self.get(node)
        resolved_node.simulation.node_bulk_reset(
            nodes=[kwargs | {'id': resolved_node.id}]
        )

    def rebuild(self, *, node: Node | PrimaryKey, **kwargs: Any) -> None:
        if isinstance(node, Node):
            resolved_node = node
        else:
            resolved_node = self.get(node)
        resolved_node.simulation.node_bulk_rebuild(
            nodes=[kwargs | {'id': resolved_node.id}]
        )
