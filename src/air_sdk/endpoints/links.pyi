# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for links endpoint type hints.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc import BaseCompatMixin
from air_sdk.endpoints.interfaces import Interface
from air_sdk.endpoints.nodes import Node
from air_sdk.endpoints.simulations import Simulation

class LinksLabels(TypedDict):
    """Properties/labels of a link."""

    cable_length: str  # NotRequired[str] (Python 3.11+)

@dataclass
class Link(BaseCompatMixin, AirModel):
    """Link model representing a network link.

    Attributes:
        id: Unique identifier for the link
        created: Timestamp when the link was created
        modified: Timestamp when the link was last modified
        interfaces: The two interfaces connected by this link
        labels: Optional labels/properties of the link (e.g. cable_length)
    """

    id: str
    created: datetime
    modified: datetime
    interfaces: list[Interface]
    labels: LinksLabels | None

    @classmethod
    def get_model_api(cls) -> type[LinkEndpointAPI]: ...
    @property
    def model_api(self) -> LinkEndpointAPI: ...
    def delete(self) -> None:
        """Delete the link.

        Example:
            >>> link.delete()
        """
        ...

class LinkEndpointAPI(BaseEndpointAPI[Link]):
    """API client for link endpoints."""

    API_PATH: str
    model: type[Link]

    def create(
        self,
        *,
        interfaces: list[Interface | PrimaryKey],
        labels: LinksLabels | None = ...,
    ) -> Link:
        """Create a new link between interfaces.

        Args:
            interfaces: The two interfaces to connect
            labels: Optional labels/properties of the link (e.g. cable_length)

        Returns:
            The created link

        Example:
            >>> link = api.links.create(interfaces=[interface1, interface2])
            >>> link = api.links.create(
            ...     interfaces=[interface1, interface2],
            ...     labels={'cable_length': '5m'},
            ... )
        """
        ...

    def list(  # type: ignore[override]
        self,
        *,
        interface: Interface | PrimaryKey = ...,
        limit: int = ...,
        node: Node | PrimaryKey = ...,
        offset: int = ...,
        search: str = ...,
        ordering: str = ...,
        simulation: Simulation | PrimaryKey = ...,
    ) -> Iterator[Link]:
        """List all links.

        Args:
            interface: Filter by specific interface
            limit: Number of results to return per page
            node: Filter by specific node
            offset: The initial index from which to return the results
            ordering: Order objects by field. Prefix with "-" for desc order
            search: Search by interface name or node name of all interfaces
                   in a case-insensitive manner
            simulation: Filter by specific simulation

        Returns:
            Iterator of Link instances

        Example:
            >>> # List all links
            >>> for link in api.links.list():
            ...     print(link.id)

            >>> # Filter by interface
            >>> for link in api.links.list(interface=interface1):
            ...     print(link.id)

            >>> # Order by creation date descending
            >>> for link in api.links.list(ordering='-created'):
            ...     print(link.id)

            >>> # Search by node name
            >>> for link in api.links.list(search='node-name'):
            ...     print(link.interfaces[0].node.name, link.interfaces[1].node.name)
        """
        ...

    def get(self, pk: PrimaryKey) -> Link:
        """Get a specific link by ID.

        Args:
            pk: The link ID (string or UUID)

        Returns:
            The Link instance

        Example:
            >>> link = api.links.get('link-id')
        """
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """Delete a specific link by ID.

        Args:
            pk: The link ID (string or UUID)

        Example:
            >>> api.links.delete('link-id')
        """
        ...
