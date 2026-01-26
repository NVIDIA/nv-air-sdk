# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for interfaces endpoint type hints.
"""

from dataclasses import _MISSING_TYPE, dataclass
from datetime import datetime
from typing import Iterator, Literal

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.nodes import Node
from air_sdk.endpoints.services import ServiceEndpointAPI

@dataclass
class InterfaceAttributes:
    interface_role: str | None
    scalable_unit: int | None

@dataclass(eq=False)
class Interface(AirModel):
    """Interface model representing a network interface.

    Attributes:
        id: Unique identifier for the interface
        name: Human-readable name of the interface
        created: Timestamp when the interface was created
        modified: Timestamp when the interface was last modified
        node: Node that the interface is related to
        interface_type: Type of the interface
        mac_address: MAC address of the interface
        connection: Interface that the interface is connected to
        outbound: Whether the interface is outbound
        attributes: Attributes of the interface
    """

    id: str
    name: str
    created: datetime
    modified: datetime
    node: Node
    interface_type: str
    mac_address: str
    connection: Interface | None
    outbound: bool
    attributes: InterfaceAttributes | None

    @classmethod
    def get_model_api(cls) -> type[InterfaceEndpointAPI]: ...
    @property
    def model_api(self) -> InterfaceEndpointAPI: ...
    def update(
        self,
        *,
        name: str | _MISSING_TYPE = ...,
        interface_type: Literal['DATA_PLANE_INTF', 'PCIE_INTF', 'OOB_INTF']
        | _MISSING_TYPE = ...,
        outbound: bool | _MISSING_TYPE = ...,
        attributes: InterfaceAttributes | None | _MISSING_TYPE = ...,
    ) -> None:
        """Update the interface's properties.

        Args:
            name: New name for the interface
            interface_type: New type for the interface
            outbound: New outbound status for the interface
            attributes: New attributes for the interface

        Example:
            >>> interface.update(name='New Name')
        """
        ...

    def delete(self) -> None:
        """Delete the interface.

        Example:
            >>> interface.delete()
        """
        ...

    def connect(self, *, target: Interface | PrimaryKey) -> Interface:
        """Connect the interface to another interface.

        Args:
            target: Interface or primary key of the interface to connect to

        Example:
            >>> interface.connect(interface)
            >>> interface.connect('interface-id')
        """
        ...
    def disconnect(self) -> Interface:
        """Disconnect the interface from its connection.

        Example:
            >>> interface.disconnect()

        """
        ...
    @property
    def services(self) -> ServiceEndpointAPI:
        # fmt: off
        """Query for the related services of the interface.

        Returns:
            ServiceEndpointAPI instance filtered for this interface's services

        Example:
            >>> for service in interface.services.list():
            ...     print(f'{service.name}: {service.worker_fqdn}:{service.worker_port}')
            >>>
            >>> # Create service on this interface
            >>> service = interface.services.create(
            ...     name='SSH', node_port=22, service_type='ssh'
            ... )
        """
        # fmt: on
        ...

class InterfaceEndpointAPI(BaseEndpointAPI[Interface]):
    """API client for interface endpoints."""

    API_PATH: str
    model: type[Interface]

    def create(
        self,
        *,
        name: str,
        node: Node | PrimaryKey,
        interface_type: Literal['DATA_PLANE_INTF', 'PCIE_INTF', 'OOB_INTF']
        | _MISSING_TYPE = ...,
        mac_address: str | _MISSING_TYPE = ...,
        outbound: bool | _MISSING_TYPE = ...,
        attributes: InterfaceAttributes | None | _MISSING_TYPE = ...,
    ) -> Interface:
        """Create a new interface.

        Args:
            name: Name of the interface
            node: Node to create the interface on

        Returns:
            The created Interface instance

        Example:
            >>> interface = api.interfaces.create(name='eth0', node=node)
            >>> interface = node.interfaces.create(name='eth0', node=node.id)

        """
        ...

    def list(  # type: ignore[override]
        self,
        *,
        interface_type: Literal['DATA_PLANE_INTF', 'PCIE_INTF', 'OOB_INTF']
        | _MISSING_TYPE = ...,
        mac_address: str | _MISSING_TYPE = ...,
        name: str | _MISSING_TYPE = ...,
        node: Node | PrimaryKey | _MISSING_TYPE = ...,
        outbound: bool | _MISSING_TYPE = ...,
        simulation: str | _MISSING_TYPE = ...,
        limit: int | _MISSING_TYPE = ...,
        offset: int | _MISSING_TYPE = ...,
        search: str | _MISSING_TYPE = ...,
        ordering: str | _MISSING_TYPE = ...,
    ) -> Iterator[Interface]:
        """List all interfaces with optional filtering.

        Args:
            interface_type: Filter by interface type
            mac_address: Filter by MAC address
            name: Filter by name
            node: Filter by node
            outbound: Filter by outbound status
            simulation: Filter by simulation
            limit: Number of results to return per page
            offset: The initial index from which to return the results
            search: Search by name
            ordering: Order by field

        Returns:
            Iterator of Interface instances

        Example:
            >>> # List all interfaces
            >>> for interface in api.interfaces.list():
            ...     print(interface.name)

            >>> # Filter by interface type
            >>> for interface in api.interfaces.list(interface_type='DATA_PLANE_INTF'):
            ...     print(interface.name)

            >>> # Search by name
            >>> for interface in api.interfaces.list(search='eth0'):
            ...     print(interface.name)

            >>> # Order by name descending
            >>> for interface in api.interfaces.list(ordering='-name'):
            ...     print(interface.name)
        """
        ...

    def update(
        self,
        *,
        interface: Interface | PrimaryKey,
        name: str | _MISSING_TYPE = ...,
        interface_type: Literal['DATA_PLANE_INTF', 'PCIE_INTF', 'OOB_INTF']
        | _MISSING_TYPE = ...,
        outbound: bool | _MISSING_TYPE = ...,
        attributes: InterfaceAttributes | None | _MISSING_TYPE = ...,
    ) -> Interface:
        # fmt: off
        """Update the interface's properties.

        Args:
            interface: Interface or primary key of the interface to update
            name: New name for the interface
            interface_type: New type for the interface
            outbound: New outbound status for the interface
            attributes: New attributes for the interface

        Returns:
            The updated Interface instance

        Example:
            >>> # Using Interface object
            >>> updated_interface = api.interfaces.update(
            ...     interface=interface, name='New Name'
            ... )
            >>> # Using interface ID
            >>> updated_interface = api.interfaces.update(
            ...     interface='interface-id',
            ...     name='New Name',
            ...     interface_type='DATA_PLANE_INTF',
            ... )
        """
        # fmt: on
        ...

    def get(self, pk: PrimaryKey) -> Interface:
        """Get a specific interface by ID.

        Args:
            pk: The interface ID (string or UUID)

        Returns:
            The Interface instance

        Example:
            >>> interface = api.interfaces.get('interface-id')
        """
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """Delete a specific interface by ID.

        Args:
            pk: The interface ID (string or UUID)

        Example:
            >>> api.interfaces.delete('interface-id')
        """
        ...

    def connect(
        self,
        *,
        interface: Interface | PrimaryKey,
        target: Interface | PrimaryKey,
    ) -> Interface:
        """Connect the interface to another interface.

        Args:
            interface: Interface or primary key of the interface to connect
            target: Interface or primary key of the interface to connect to

        Returns:
            The source interface instance

        Example:
            >>> api.interfaces.connect(interface=interface, target=target)
            >>> api.interfaces.connect(interface='interface-id', target='target-id')
        """
        ...

    def disconnect(self, *, interface: Interface | PrimaryKey) -> Interface:
        """Disconnect the interface from its connection.

        Args:
            interface: Interface or primary key of the interface to disconnect

        Returns:
            The source interface instance

        Example:
            >>> api.interfaces.disconnect(interface=interface)
            >>> api.interfaces.disconnect(interface='interface-id')
        """
        ...
