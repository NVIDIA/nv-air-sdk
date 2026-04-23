# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for interfaces endpoint type hints.
"""

from dataclasses import _MISSING_TYPE, dataclass
from datetime import datetime
from typing import Iterator, List, Literal

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.links import LinkEndpointAPI
from air_sdk.endpoints.nodes import Node
from air_sdk.endpoints.services import ServiceEndpointAPI

@dataclass
class InterfaceLabels:
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
        labels: Labels of the interface
        interface_role: The role of the interface
        scalable_unit: The scalable unit number of the interface
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
    labels: InterfaceLabels | None
    interface_role: str | None
    scalable_unit: int | None

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
        labels: InterfaceLabels | None | _MISSING_TYPE = ...,
        interface_role: str | None | _MISSING_TYPE = ...,
        scalable_unit: int | None | _MISSING_TYPE = ...,
    ) -> None:
        """Update the interface's properties.

        Args:
            name: New name for the interface
            interface_type: New type for the interface
            outbound: New outbound status for the interface
            labels: New labels for the interface
            interface_role: New role for the interface
            scalable_unit: New scalable unit for the interface

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

    @property
    def links(self) -> LinkEndpointAPI:
        """Access the links endpoint for this interface.

        Returns:
            LinkEndpointAPI instance filtered for this interface's links

        Example:
            >>> for link in interface.links.list():
            ...     print(link.id)
        """
        ...
    def breakout(self, *, split_count: int) -> List[Interface]:
        """Break out this interface into multiple sub-interfaces.

        Args:
            split_count: Number of interfaces to create from the breakout.
                Must be supported by the node's split_options.

        Returns:
            List of created breakout interfaces

        Example:
            >>> interface = api.interfaces.get('interface-id')
            >>> breakout_interfaces = interface.breakout(split_count=4)
            >>> # Creates swp1s0, swp1s1, swp1s2, swp1s3
        """
        ...
    def revert_breakout(self) -> Interface:
        """Revert this breakout interface back to a single interface.

        Can be called on any of the breakout interfaces - they will all be
        reverted and deleted except the first one (s0), which will be renamed
        back to the original name.

        Returns:
            The reverted interface

        Example:
            >>> interface = api.interfaces.get('interface-id')  # e.g., swp1s0
            >>> reverted = interface.revert_breakout()  # Reverts back to swp1

        Note:
            - All breakout interfaces will be deleted except the first one (s0)
            - The s0 interface will be renamed back to the original name
            - Any existing connections on the breakout interfaces are
              automatically removed
            - Cannot revert if any breakout interface has services attached
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
        labels: InterfaceLabels | None | _MISSING_TYPE = ...,
        interface_role: str | None | _MISSING_TYPE = ...,
        scalable_unit: int | None | _MISSING_TYPE = ...,
    ) -> Interface:
        """Create a new interface.

        Args:
            name: Name of the interface
            node: Node to create the interface on
            interface_type: Type of the interface
            mac_address: MAC address of the interface
            outbound: Outbound status of the interface
            labels: Labels for the interface
            interface_role: Role of the interface
            scalable_unit: Scalable unit of the interface

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

    def breakout(
        self, *, interface: Interface | PrimaryKey, split_count: int
    ) -> List[Interface]:
        # fmt: off
        """Break out an interface into multiple sub-interfaces.

        Breaks out a data plane interface into multiple sub-interfaces.
        For example, breaking out "swp1" with a 4-way split creates
        "swp1s0", "swp1s1", "swp1s2", "swp1s3".

        Args:
            interface: The interface to break out
            split_count: Number of interfaces to create from the breakout.
                Must be supported by the node's split_options (typically 2, 4, or 8).

        Returns:
            List of all created breakout interfaces

        Example:
            >>> interface = api.interfaces.get('interface-id')
            >>> breakout_interfaces = api.interfaces.breakout(  # fmt: skip
            ...     interface=interface, split_count=4
            ... )
            >>> print([i.name for i in breakout_interfaces])
            ['swp1s0', 'swp1s1', 'swp1s2', 'swp1s3']

        Note:
            - Only data plane interfaces can be broken out
            - Any existing connection on the interface will be automatically removed
            - The original interface is renamed to <name>s0 and keeps its MAC address
            - New interfaces are created with allocated MAC addresses
        """
        # fmt: on
        ...
    def revert_breakout(self, *, interface: Interface | PrimaryKey) -> Interface:
        """Revert a broken out interface back to a single interface.

        Reverts broken out interfaces back to a single interface.
        For example, reverting "swp1s0" (along with "swp1s1", "swp1s2", "swp1s3")
        back to "swp1". This can be called on any of the breakout interfaces.

        Args:
            interface: One of the breakout interfaces (e.g., swp1s0, swp1s1, etc.)

        Returns:
            The reverted interface with its original name

        Example:
            >>> interface = api.interfaces.get('interface-id')  # e.g., swp1s2
            >>> reverted = api.interfaces.revert_breakout(interface=interface)
            >>> print(reverted.name)
            'swp1'

        Note:
            - All breakout interfaces will be deleted except the first one (s0)
            - The s0 interface will be renamed back to the original name
            - Any existing connections on the breakout interfaces are
              automatically removed
            - Cannot revert if any breakout interface has services attached
        """
        ...
