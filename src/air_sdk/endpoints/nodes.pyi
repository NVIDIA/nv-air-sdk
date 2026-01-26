# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for simulations endpoint type hints.
"""

from dataclasses import _MISSING_TYPE, dataclass
from datetime import datetime
from typing import Any, Iterator, Literal, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc.cloud_init import CloudInit
from air_sdk.endpoints import UserConfig
from air_sdk.endpoints.images import Image
from air_sdk.endpoints.interfaces import InterfaceEndpointAPI
from air_sdk.endpoints.services import Service, ServiceEndpointAPI
from air_sdk.endpoints.simulations import Simulation
from air_sdk.endpoints.systems import System

class NodeAttributes(TypedDict, total=False):
    """Node attributes for topology organization."""

    group: str | None
    model: str | None
    sku: str | None
    rack_name: str | None
    rack_unit: int | None
    scalable_unit: int | None
    rail_index: int | None
    data_hall: str | None
    tray_index: int | None
    role: str | None
    pod: int | None
    superspine_group: int | None
    plane_id: int | None

class NodeAdvanced(TypedDict, total=False):
    """Advanced node configuration options."""

    secureboot: bool | None
    uefi: bool | None
    tpm: bool | None
    cpu_options: Literal['ssse3', 'sse4.1', 'sse4.2', 'popcnt'] | None
    cpu_mode: Literal['custom', 'host-model', 'host-passthrough']
    boot: Literal['hd', 'network']
    nic_model: Literal['virtio', 'e1000']

class NodeCDROM(TypedDict, total=False):
    """CD-ROM configuration for a node."""

    image: Image | None

class StoragePCIField(TypedDict, total=False):
    """Represents a single storage PCI drive configuration.

    Used in storage_pci as: dict[str, StoragePCIField]
    where keys are dynamic drive names like "drive1", "drive2", etc.
    """

    name: str | None
    size: int | None
    type: Literal['NVME'] | None

class CloudInitAssignment(TypedDict):
    """Response payload for cloud-init assignment."""

    user_data: UserConfig | None
    meta_data: UserConfig | None

@dataclass(eq=False)
class Node(AirModel):
    """Node model representing a network node.

    Attributes:
        id: Unique identifier for the node
        name: Human-readable name of the node
        created: Timestamp when the node was created
        modified: Timestamp when the node was last modified
        state: Current state of the node
        category: Category of the node
        status_from_worker: Status of the node from the worker
        split_options: Split options for the node
        cpu: CPU of the node
        memory: Memory of the node
        storage: Storage of the node
        pos_x: X position of the node
        pos_y: Y position of the node
        attributes: Attributes of the node
        advanced: Advanced attributes of the node
        cdrom: CDROM attributes of the node
        storage_pci: Storage PCI attributes of the node
        cloud_init: Cloud-Init assignments of the node
    """

    id: str
    created: datetime
    modified: datetime
    name: str
    simulation: Simulation
    image: Image
    state: str
    category: str
    status_from_worker: str
    split_options: list[int] | None
    cpu: int
    memory: int
    storage: int
    pos_x: int
    pos_y: int
    attributes: NodeAttributes | None
    advanced: NodeAdvanced
    cdrom: NodeCDROM | None
    storage_pci: dict[str, StoragePCIField] | None

    @classmethod
    def get_model_api(cls) -> type[NodeEndpointAPI]: ...
    @property
    def model_api(self) -> NodeEndpointAPI: ...
    def update(
        self,
        *,
        name: str | _MISSING_TYPE = ...,
        image: Image | _MISSING_TYPE = ...,
        cpu: int | _MISSING_TYPE = ...,
        memory: int | _MISSING_TYPE = ...,
        storage: int | _MISSING_TYPE = ...,
        pos_x: int | _MISSING_TYPE = ...,
        pos_y: int | _MISSING_TYPE = ...,
        attributes: dict[str, Any] | _MISSING_TYPE = ...,
        advanced: dict[str, Any] | _MISSING_TYPE = ...,
        storage_pci: dict[str, Any] | _MISSING_TYPE = ...,
    ) -> None:
        """Update the node's properties.

        Args:
            name: Name of the node
            image: Image of the node
            cpu: CPU of the node
            memory: Memory of the node
            storage: Storage of the node
            pos_x: X position of the node
            pos_y: Y position of the node
            attributes: Attributes of the node
            advanced: Advanced attributes of the node
            storage_pci: Storage PCI of the node

        Example:
            >>> node = api.nodes.update(
            ...     name='my-node',
            ...     image=image,
            ...     cpu=1,
            ...     memory=1024,
            ...     storage=10,
            ...     pos_x=0,
            ...     pos_y=0,
            ...     attributes={'key': 'value'},
            ...     advanced={'key': 'value'},
            ...     storage_pci={'key': 'value'},
            ... )
        """
        ...

    def clear_cloud_init_assignment(self, **kwargs: Any) -> None:
        """Clear cloud-init assignment for this node (V3).

        Removes any user_data and meta_data cloud-init configurations from this node.

        Example:
            >>> node.clear_cloud_init_assignment()
        """
        ...

    @property
    def instructions(self) -> Any:
        """Access the instructions endpoint for this node.

        Returns:
            Any instance scoped to this node

        Example:
            >>> node = api.nodes.instructions.list()
        """
        ...

    @property
    def interfaces(self) -> InterfaceEndpointAPI:
        """Access the interfaces endpoint for this node.

        Returns:
            Any instance scoped to this node

        Example:
            >>> for interface in node.interfaces.list():
            ...     print(interface.name)
        """
        ...

    @property
    def services(self) -> ServiceEndpointAPI:
        # fmt: off
        """Query for the related services of the node.

        Returns:
            ServiceEndpointAPI instance filtered for this node's services

        Example:
            >>> for service in node.services.list():
            ...     print(f'{service.name}: {service.worker_fqdn}:{service.worker_port}')
            >>>
            >>> # Create service by interface ID
            >>> service = node.services.create(
            ...     name='ssh-service',
            ...     interface='interface-id',
            ...     node_port=22,
            ...     service_type='SSH'
            ... )
        """
        ...
        # fmt: on
    def create_service(
        self,
        *,
        interface_name: str,
        node_port: int,
        name: str = ...,
        service_type: Literal['SSH', 'HTTPS', 'HTTP', 'OTHER'] = ...,
    ) -> Service:
        """Create service by resolving interface name (v3 convenience).

        Args:
            interface_name: Interface name on this node (e.g., 'eth0', 'swp1')
            node_port: Port number on the node/interface
            name: Service name
            service_type: Service type - 'SSH', 'HTTPS', 'HTTP', or 'OTHER'

        Returns:
            Service object

        Raises:
            ValueError: If interface not found on this node

        Example:
            >>> service = node.create_service(
            ...     interface_name='eth0',
            ...     name='ssh-service',
            ...     node_port=22,
            ...     service_type='SSH',
            ... )
        """
        ...

    def delete_all_node_instructions(self) -> None:
        """Delete all node instructions for this node.

        Example:
            >>> node = api.nodes.delete_all_node_instructions()
        """
        ...

    @property
    def cloud_init(self) -> CloudInit:
        """Get the cloud-init assignment for this node.

        Returns:
            CloudInit object containing user_data and meta_data assignments

        Example:
            >>> cloud_init = node.cloud_init
            >>> print(cloud_init.user_data)
            >>> print(cloud_init.meta_data)
        """
        ...

    def reset(self) -> None:
        """Reset this node.

        Resetting the node emulates the hardware reset button on physical machines
        where the machine is immediately restarted without a clean shutdown of the
        operating system. For nodes that are not currently running, this means simply
        booting them back up.

        Example:
            >>> node.reset()
        """
        ...

    def rebuild(self) -> None:
        """Rebuild this node.

        Rebuilding a node means returning the node to the state of its simulation's
        current checkpoint.
        When rebuilding from the initial state, all repeatable instructions
        for this node will be applied. All existing instructions created for this node
        which have not yet been completed will be failed. All existing instructions
        created for this node which have not yet been delivered will be cancelled.

        Example:
            >>> node.rebuild()
        """
        ...

class NodeEndpointAPI(BaseEndpointAPI[Node]):
    """API client for simulation endpoints."""

    API_PATH: str
    model: type[Node]

    def create(
        self,
        *,
        name: str,
        simulation: Simulation,
        image: Image,
        cpu: int | None = ...,
        memory: int | None = ...,
        storage: int | None = ...,
        pos_x: int | None = ...,
        pos_y: int | None = ...,
        attributes: NodeAttributes | None = ...,
        advanced: NodeAdvanced | None = ...,
        storage_pci: dict[str, StoragePCIField] | None = ...,
    ) -> Node:
        """Create a new node.

        Args:
            name: Name of the node
            simulation: Simulation of the node
            image: Image of the node
            cpu: (optional) CPU of the node
            memory: (optional) Memory of the node
            storage: (optional) Storage of the node
            pos_x: (optional) X position of the node
            pos_y: (optional) Y position of the node
            attributes: (optional) Attributes of the node
            advanced: (optional) Advanced attributes of the node
            storage_pci: (optional) Storage PCI of the node

        Returns:
            The created node instance

        Example
        -------
            >>> node = api.nodes.create(simulation=sim, image=image, name='my-node')
        """

    def list(
        self,
        *,
        limit: int | None = ...,
        offset: int | None = ...,
        ordering: str | None = ...,
        search: str | None = ...,
        **kwargs: Any,
    ) -> Iterator[Node]:
        """List all nodes.

        Args:
            limit: (optional) Limit the number of nodes returned
            offset: (optional) Offset the number of nodes returned
            ordering: (optional) Order the nodes by a field
            search: (optional) Search for nodes by a keyword

        Returns:
            Iterator of Node instances

        Example:
            >>> for node in api.nodes.list(ordering='name'):
            ...     print(node.name)

            >>> for node in api.nodes.list(search='my-node'):
            ...     print(node.name)

            >>> for node in api.nodes.list(ordering='-name'):
            ...     print(node.name)
        """

    def get(self, pk: PrimaryKey) -> Node:
        """Get a specific node by ID.

        Args:
            pk: The node ID (string or UUID)

        Returns:
            The Node instance

        Example:
            >>> node = api.nodes.get('node-id')
        """
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """Delete a specific node by ID.

        Args:
            pk: The node ID (string or UUID)

        Example:
            >>> api.nodes.delete('node-id')
        """

    def update(
        self,
        *,
        node: Node | PrimaryKey,
        name: str | _MISSING_TYPE = ...,
        image: Image | _MISSING_TYPE = ...,
        cpu: int | _MISSING_TYPE = ...,
        memory: int | _MISSING_TYPE = ...,
        storage: int | _MISSING_TYPE = ...,
        pos_x: int | _MISSING_TYPE = ...,
        pos_y: int | _MISSING_TYPE = ...,
        attributes: NodeAttributes | _MISSING_TYPE = ...,
        advanced: NodeAdvanced | _MISSING_TYPE = ...,
        storage_pci: dict[str, StoragePCIField] | None = ...,
    ) -> Node:
        """Update a specific node by ID.

        Args:
            node: The node to update (Node object or ID)
            name: Name of the node
            image: Image of the node (image object or ID)
            cpu: CPU of the node
            memory: Memory of the node
            storage: Storage of the node
            pos_x: X position of the node
            pos_y: Y position of the node
            attributes: Attributes of the node
            advanced: Advanced attributes of the node
            storage_pci: Storage PCI of the node

        Example:
            >>> node = api.nodes.update(node=node, name='my-node')
        """
        ...

    def create_from_system_node(
        self,
        system_node: System | PrimaryKey,
        name: str,
        simulation: Simulation | PrimaryKey,
        image: Image | PrimaryKey | _MISSING_TYPE = ...,
        cpu: int | _MISSING_TYPE = ...,
        memory: int | _MISSING_TYPE = ...,
        storage: int | _MISSING_TYPE = ...,
        pos_x: int | _MISSING_TYPE = ...,
        pos_y: int | _MISSING_TYPE = ...,
        attributes: dict[str, Any] | _MISSING_TYPE = ...,
        advanced: dict[str, Any] | _MISSING_TYPE = ...,
        storage_pci: dict[str, StoragePCIField] | _MISSING_TYPE = ...,
        **kwargs: Any,
    ) -> Node:
        # fmt: off
        """Create a node from a system node template.

        Args:
            system_node: System node template ID to create from
            name: Name of the new node
            simulation: Simulation object or ID where the node will be created
            image: Optional image to use (overrides template)
            cpu: Optional CPU count (overrides template)
            memory: Optional memory in MB (overrides template)
            storage: Optional storage in GB (overrides template)
            pos_x: Optional X position on canvas
            pos_y: Optional Y position on canvas
            attributes: Optional node attributes
            advanced: Optional advanced configuration
            storage_pci: Optional storage PCI configuration
            **kwargs: Additional parameters

        Returns:
            The created Node object
        Example:
            >>> node = api.nodes.from_system_node(
            ...     system_node='system-node-template-id',
            ...     name='my-node',
            ...     simulation='simulation-id'
            ... )
        """
        ...
        # fmt: on
    def list_system_nodes(self, **kwargs: Any) -> list[System]:  # type: ignore[valid-type]
        """List all available system nodes.

        Args:
            limit: (optional) Limit the number of system nodes returned
            offset: (optional) Offset the number of system nodes returned
            ordering: (optional) Order the system nodes by a field
            search: (optional) Search for system nodes by a keyword
            simulation: (optional) Filter system nodes by simulation

        Returns:
            List of System objects that can be used to create nodes.
        """
        ...

    def reset(self, *, node: Node | PrimaryKey) -> None:
        """Reset a node.

        Resetting the node emulates the hardware reset button on physical machines
        where the machine is immediately restarted without a clean shutdown of the
        operating system. For nodes that are not currently running, this means simply
        booting them back up.

        Args:
            node: The node object or node ID to reset

        Example:
            >>> # Reset using node object
            >>> api.nodes.reset(node=node)

            >>> # Reset using node ID
            >>> api.nodes.reset(node='node-uuid-123')
        """
        ...

    def rebuild(self, *, node: Node | PrimaryKey) -> None:
        """Rebuild a node.

        Rebuilding a node means returning the node to the state of its simulation's
        current checkpoint.
        When rebuilding from the initial state, all repeatable instructions
        for the node will be applied. All existing instructions created for the node
        which have not yet been completed will be failed. All existing instructions
        created for the node which have not yet been delivered will be cancelled.

        Args:
            node: The node object or node ID to rebuild

        Example:
            >>> # Rebuild using node object
            >>> api.nodes.rebuild(node=node)

            >>> # Rebuild using node ID
            >>> api.nodes.rebuild(node='node-uuid-123')
        """
        ...
