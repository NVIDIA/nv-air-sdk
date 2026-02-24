# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for systems endpoint type hints.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey

if TYPE_CHECKING:
    from air_sdk.endpoints.images import Image
    from air_sdk.endpoints.simulations import Simulation

@dataclass(eq=False)
class System(AirModel):
    """System model representing a system in the AIR platform."""

    id: str
    created: datetime
    modified: datetime
    name: str
    simulation: Simulation | None
    image: Image
    memory: int
    storage: int
    cpu: int
    category: str
    attributes: dict[str, Any]
    split_options: list[int] | None

    @classmethod
    def get_model_api(cls) -> type[SystemEndpointAPI]: ...
    @property
    def model_api(self) -> SystemEndpointAPI: ...

class SystemEndpointAPI(BaseEndpointAPI[System]):
    """API client for System endpoints."""

    API_PATH: str
    model: type[System]

    def list(  # type: ignore[override]
        self,
        *,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
        attributes__group: str = ...,
        attributes__model: str = ...,
        attributes__sku: str = ...,
        category: str = ...,
        id: str = ...,
        image: Image | PrimaryKey = ...,
        name: str = ...,
        simulation: Simulation | PrimaryKey = ...,
    ) -> Iterator[System]:
        """List all systems with optional filtering.

        Args:
            limit: Maximum number of results to return per page
            offset: The initial index from which to return the results
            ordering: Order objects by field. Prefix with "-" for desc order
            search: Search by name
            attributes__group: Filter by group
            attributes__model: Filter by model
            attributes__sku: Filter by sku
            category: Filter by category
            id: Filter by ID
            image: Filter by image
            simulation: Filter by simulation

        Returns:
            Iterator of System instances

        Example:
            >>> # List all systems
            >>> for system in api.systems.list():
            ...     print(system.name)

            >>> # Search by name
            >>> for system in api.systems.list(search='my-system'):
            ...     print(system.name)

            >>> # Order by name descending
            >>> for system in api.systems.list(ordering='-name'):
            ...     print(system.name)
        """
        ...

    def get(self, pk: PrimaryKey) -> System:
        """Get a specific system by ID.

        Args:
            pk: The system ID (string or UUID)

        Returns:
            The System instance

        Example:
            >>> system = api.systems.get('system-id')
            >>> print(system.name)
        """
        ...
