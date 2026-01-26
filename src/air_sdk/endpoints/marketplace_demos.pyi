# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for marketplace demos endpoint type hints.
"""

from dataclasses import _MISSING_TYPE, dataclass
from datetime import datetime
from typing import Any, Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.simulations import Simulation

@dataclass(eq=False)
class MarketplaceDemo(AirModel):
    """Marketplace demo model representing a marketplace demo.

    Attributes:
        id: Unique identifier for the marketplace demo
        name: Human-readable name of the marketplace demo
        created: Timestamp when the marketplace demo was created
        modified: Timestamp when the marketplace demo was last modified
        creator: The creator of the marketplace demo
        description: The description of the demo
        documentation: The documentation of the marketplace demo
        repo: The repository of the marketplace demo
        tags: The tags of the marketplace demo
        like_count: How many unique users have liked the marketplace demo
        liked_by_client: Whether the current user has liked the marketplace demo
        published: Whether the marketplace demo is published
        icon: The icon of the marketplace demo
        demo: Demo simulation to be used as a base for cloned simulations.
    """

    id: str
    name: str
    demo: Simulation
    created: datetime
    modified: datetime
    creator: str
    documentation: str | None
    tags: list[str]
    like_count: int
    liked_by_client: bool
    published: bool
    description: str | None
    repo: str | None
    icon: str | None

    @classmethod
    def get_model_api(cls) -> type[MarketplaceDemoEndpointAPI]: ...
    @property
    def model_api(self) -> MarketplaceDemoEndpointAPI: ...
    def update(  # type: ignore[override]
        self,
        *,
        name: str | _MISSING_TYPE = ...,
        description: str | None | _MISSING_TYPE = ...,
        documentation: str | None | _MISSING_TYPE = ...,
        repo: str | None | _MISSING_TYPE = ...,
        tags: list[str] | _MISSING_TYPE = ...,
        icon: str | None | _MISSING_TYPE = ...,
    ) -> MarketplaceDemo:
        """
        Update the marketplace demo's properties.

        Args:
            name: New name for the marketplace demo
            description: Description of the marketplace demo
            documentation: Documentation of the marketplace demo
            repo: Repository of the marketplace demo
            tags: Tags of the marketplace demo
            icon: Icon of the marketplace demo

        Returns:
            The updated MarketplaceDemo instance

        Example:
            >>> marketplace_demo.update(name='New Name', description='New Desc')
            >>> print(marketplace_demo.name)
        """
        ...

    def publish(self, **kwargs: Any) -> None:
        """
        Publish the marketplace demo.

        Example:
            >>> marketplace_demo.publish()
        """
        ...

    def unpublish(self, **kwargs: Any) -> None:
        """
        Unpublish the marketplace demo.

        Example:
            >>> marketplace_demo.unpublish()
        """
        ...

    def provision(self, **kwargs: Any) -> Simulation:
        """
        Provision a simulation from this marketplace demo.

        Returns:
            Simulation: The newly created simulation instance.

        Example:
            >>> simulation = marketplace_demo.provision()
            >>> print(simulation.name)
        """
        ...

class MarketplaceDemoEndpointAPI(BaseEndpointAPI[MarketplaceDemo]):
    """
    API client for marketplace demo endpoints."""

    API_PATH: str
    model: type[MarketplaceDemo]

    def create(
        self,
        *,
        name: str,
        simulation: str,
        description: str | None | _MISSING_TYPE = ...,
        documentation: str | None | _MISSING_TYPE = ...,
        repo: str | None | _MISSING_TYPE = ...,
        tags: list[str] | _MISSING_TYPE = ...,
        icon: str | None | _MISSING_TYPE = ...,
        checkpoint: str | None | _MISSING_TYPE = ...,
    ) -> MarketplaceDemo:
        """
        Create a new marketplace demo.

        Args:
            name: Name for the new marketplace demo
            simulation: Simulation to be used to provision the marketplace demo
            description: Description of the marketplace demo
            documentation: Documentation of the marketplace demo
            repo: Repository of the marketplace demo
            tags: Tags of the marketplace demo
            icon: Icon of the marketplace demo
            checkpoint: A COMPLETE checkpoint to clone from.
                       Provided checkpoint must belong to the simulation.
                       If not specified, latest COMPLETE checkpoint will be used.

        Returns:
            The created MarketplaceDemo instance

        Example:
            >>> marketplace_demo = api.marketplace_demos.create(
            ...     name='My Marketplace Demo',
            ...     simulation='sim-id',
            ...     description='My Demo Description',
            ...     documentation='My Demo Documentation',
            ...     repo='My Demo Repo',
            ...     tags=['networking', 'sonic'],
            ... )

        """
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """
        Delete a marketplace demo.

        Args:
            pk: The marketplace demo ID (string or UUID)

        Example:
            >>> api.marketplace_demos.delete('marketplace-demo-id')
        """
        ...

    def list(  # type: ignore[override]
        self,
        *,
        creator: str | _MISSING_TYPE = ...,
        published: bool | _MISSING_TYPE = ...,
        tags: list[str] | _MISSING_TYPE = ...,
        search: str | _MISSING_TYPE = ...,
        ordering: str | _MISSING_TYPE = ...,
        liked_by_client: bool | _MISSING_TYPE = ...,
        limit: int | _MISSING_TYPE = ...,
        offset: int | _MISSING_TYPE = ...,
    ) -> Iterator[MarketplaceDemo]:
        """
        List all marketplace demos.

        Optional parameters:
            creator: Filter by creator email
            published: Filter by published status
            tags: Filter by tags
            search: Search term to filter demos
            ordering: Order the response by the specified field
            liked_by_client: Filter by liked by client status
            limit: Number of results to return per page
            offset: The initial index from which to return the results

        Returns:
            Iterator of MarketplaceDemo instances

        Example:
            >>> # List all demos
            >>> for demo in api.marketplace_demos.list():
            ...     print(demo.name)
            >>> # List with filters
            >>> results = list(
            ...     api.marketplace_demos.list(
            ...         creator='test@example.com',
            ...         published=True,
            ...         tags=['networking'],
            ...     )
            ... )

        """
        ...

    def get(self, pk: PrimaryKey) -> MarketplaceDemo:
        """
        Get a specific marketplace demo by ID.

        Args:
            pk: The marketplace demo ID (string or UUID)

        Returns:
            The MarketplaceDemo instance

        Example:
            >>> marketplace_demo = api.marketplace_demos.get('marketplace-demo-id')
            >>> print(marketplace_demo.name)

        """
        ...

    def publish(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> None:
        """
        Publish a marketplace demo.

        Args:
            marketplace_demo: The marketplace demo to publish (object or ID)

        Returns:
            None

        Example:
            >>> # Using demo object
            >>> api.marketplace_demos.publish(marketplace_demo=marketplace_demo)
            >>> # Or using ID
            >>> api.marketplace_demos.publish(marketplace_demo='marketplace-demo-id')

        """
        ...

    def unpublish(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> None:
        """
        Unpublish a marketplace demo.

        Args:
            marketplace_demo: The marketplace demo to unpublish (object or ID)

        Returns:
            None

        Example:
            >>> api.marketplace_demos.unpublish(marketplace_demo=marketplace_demo)

        """
        ...

    def provision(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> Simulation:
        """
        Provision a simulation from a marketplace demo.

        Creates a new simulation by cloning the demo simulation.

        Args:
            marketplace_demo: The marketplace demo to provision (object or ID)

        Returns:
            Simulation: The newly created simulation instance.

        Example:
            >>> # Using demo object
            >>> marketplace_demo = api.marketplace_demos.get('marketplace-demo-id')
            >>> simulation = marketplace_demo.provision()
            >>> print(simulation.id)
            >>> # Or using API directly with ID
            >>> demo_id = 'marketplace-demo-id'
            >>> simulation = api.marketplace_demos.provision(marketplace_demo=demo_id)
            >>> print(simulation.name)

        """
        ...
