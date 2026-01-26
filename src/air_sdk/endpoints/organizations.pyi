# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for organizations / resource budgets endpoint type hints.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.types import ResourceBudgetUsage

@dataclass(eq=False)
class Organization(AirModel):
    """Represents an organization and its resource budget in the Air platform.

    This model combines organization metadata with resource budget information.

    Attributes:
        id: Unique identifier for the resource budget
        created: Timestamp when the resource budget was created
        modified: Timestamp when the resource budget was last modified
        org_display_name: Display name of the organization
        org_nca_id: NCA ID of the organization
        cpu: Number of CPU cores allocated
        memory: Memory allocated, in MiB
        disk_storage_total: Total disk storage allocated, in GB
        disk_storage_per_node: Disk storage per node, in GB
        image_storage: Image storage allocated, in GB
        userconfigs: Total UserConfig content allocated, in bytes
        usage: Current resource usage
    """

    id: str
    created: datetime
    modified: datetime
    org_display_name: str
    org_nca_id: str
    cpu: int | float
    memory: int | float
    disk_storage_total: int | float
    disk_storage_per_node: int
    image_storage: int
    userconfigs: int
    usage: ResourceBudgetUsage

    @property
    def name(self) -> str:
        """Organization name (alias for org_display_name)."""
        ...

    @classmethod
    def get_model_api(cls) -> type[OrganizationEndpointAPI]: ...
    @property
    def model_api(self) -> OrganizationEndpointAPI: ...

class OrganizationEndpointAPI(BaseEndpointAPI[Organization]):
    """API client for Organization / ResourceBudget endpoints.

    This endpoint is read-only and provides access to organization
    resource budget information.

    Also aliased as ResourceBudgetEndpointAPI.
    """

    API_PATH: str
    model: type[Organization]

    def list(  # type: ignore[override]
        self,
        *,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        org_display_name: str = ...,
        org_nca_id: str = ...,
        search: str = ...,
    ) -> Iterator[Organization]:
        """List all organizations / resource budgets with optional filtering.

        Args:
            limit: Maximum number of results to return per page
            offset: The initial index from which to return the results
            ordering: Order by field. Prefix with "-" for descending order
            org_display_name: Filter by the display name of the organization
            org_nca_id: Filter by the NCA ID of the organization
            search: Search resource budgets by org_display_name

        Returns:
            Iterator of Organization instances

        Example:
            >>> # List all organizations
            >>> for org in api.organizations.list():
            ...     print(org.name, org.org_nca_id)

            >>> # Filter by org_nca_id
            >>> for org in api.organizations.list(org_nca_id='nca-123'):
            ...     print(org.name)

            >>> # Search by name
            >>> for org in api.organizations.list(search='NVIDIA'):
            ...     print(org.name)
        """
        ...

    def get(self, pk: PrimaryKey) -> Organization:
        """Get a specific organization / resource budget by ID.

        Args:
            pk: The resource budget ID (string or UUID)

        Returns:
            The Organization instance

        Example:
            >>> org = api.organizations.get('b4d0480c-6f0b-4c40-b143-c141531fc14e')
            >>> print(org.name, org.cpu, org.memory)
        """
        ...

# Aliases
ResourceBudget = Organization
ResourceBudgetEndpointAPI = OrganizationEndpointAPI
