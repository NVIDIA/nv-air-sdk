# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Literal

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc import BaseCompatMixin, ServiceCompatMixin, ServiceEndpointAPICompatMixin
from air_sdk.endpoints import mixins
from air_sdk.endpoints.interfaces import Interface

@dataclass(eq=False)
class Service(ServiceCompatMixin, BaseCompatMixin, AirModel):
    """Represents a service in the Air API.

    A service exposes a port on a simulation interface to external networks,
    enabling connectivity between simulations and the outside world.

    Attributes:
        id: Unique identifier
        name: Service name
        node_port: Port number on the node/interface
        interface: Interface object (foreign key relationship)
        service_type: Type of service (e.g., 'ssh', 'http', 'https')
        worker_port: External port on the worker (assigned by Air)
        worker_fqdn: Fully qualified domain name of the worker
        created: Timestamp when service was created
        modified: Timestamp when service was last modified

    Example:
        >>> # Access service details
        >>> print(f'Service: {service.name}')
        >>> print(f'Connect via: {service.worker_fqdn}:{service.worker_port}')
        >>> print(f'Interface: {service.interface.name}')
        >>>
        >>> # Delete service
        >>> service.delete()
    """

    id: str
    name: str
    node_port: int
    interface: Interface
    service_type: str
    worker_port: int | None
    worker_fqdn: str | None
    created: datetime
    modified: datetime

    @classmethod
    def get_model_api(cls) -> type[ServiceEndpointAPI]: ...

    # NOTE: Services are immutable after creation in the Air API.
    # There is no update() method. To change a service, delete and recreate it.

    def delete(self) -> None:
        """Delete the service.

        After deletion, the service object should not be used.

        Example:
            >>> service.delete()
        """
        ...

    def refresh(self) -> None:
        """Refresh service data from the API.

        Example:
            >>> service.refresh()
        """
        ...

class ServiceEndpointAPI(
    ServiceEndpointAPICompatMixin,
    mixins.ListApiMixin[Service],
    mixins.CreateApiMixin[Service],
    mixins.GetApiMixin[Service],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Service],
):
    """API for managing services.

    Services expose ports on simulation interfaces to enable external connectivity.

    Example:
        >>> # List all services
        >>> for service in api.services.list():
        ...     print(f'{service.name}: {service.worker_fqdn}:{service.worker_port}')
        >>>
        >>> # Create a service
        >>> interface = api.interfaces.get('interface-id')
        >>> service = api.services.create(
        ...     name='SSH Service',
        ...     node_port=22,
        ...     interface=interface,
        ...     service_type='ssh',
        ... )
        >>>
        >>> # Get a service
        >>> service = api.services.get('service-id')
        >>>
        >>> # Delete a service
        >>> api.services.delete(service)
    """

    API_PATH: str
    model: type[Service]

    # fmt: off
    def list(  # type: ignore[override]
        self,
        *,
        interface: PrimaryKey | None = ...,
        name: str | None = ...,
        node_port: int | None = ...,
        worker_port: int | None = ...,
        worker_fqdn: str | None = ...,
        service_type: str | None = ...,
        search: str | None = ...,
        ordering: str | None = ...,
        limit: int | None = ...,
        offset: int | None = ...,
    ) -> Iterator[Service]:
        """List services with optional filtering and pagination.

        Args:
            interface: Filter by interface ID or instance
            name: Filter by service name
            node_port: Filter by node port
            worker_port: Filter by worker port
            worker_fqdn: Filter by worker FQDN
            service_type: Filter by service type (ssh, http, https, etc.)
            search: Search term to filter results
            ordering: Field to order results by (prefix with '-' for descending)
            limit: Maximum number of results to return
            offset: Number of results to skip

        Yields:
            Service instances

        Example:
            >>> # List all services
            >>> for service in api.services.list():
            ...     print(service.name)
            >>>
            >>> # Filter by interface
            >>> for service in api.services.list(interface='interface-id'):
            ...     print(f"{service.name}: {service.worker_port}")
            >>>
            >>> # Filter by service type
            >>> for service in api.services.list(service_type='ssh'):
            ...     print(service.name)
        """
        ...
    # fmt: on
    def get(self, pk: PrimaryKey) -> Service:  # type: ignore[override]
        """Get a service by ID.

        Args:
            pk: Service ID

        Returns:
            Service instance

        Raises:
            AirUnexpectedResponse: Service not found or API error

        Example:
            >>> service = api.services.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
            >>> print(f'{service.name}: {service.worker_fqdn}:{service.worker_port}')
        """
        ...

    def create(
        self,
        *,
        name: str,
        node_port: int,
        interface: PrimaryKey,
        service_type: Literal['SSH', 'HTTPS', 'HTTP', 'OTHER'] = ...,
    ) -> Service:
        """Create a new service.

        Args:
            name: Service name
            node_port: Port number on the node/interface
            interface: Interface instance or ID
            service_type: Service type - 'SSH', 'HTTPS', 'HTTP', or 'OTHER'

        Returns:
            Created Service instance

        Raises:
            AirUnexpectedResponse: Creation failed

        Example:
            >>> service = api.services.create(
            ...     name='SSH Access',
            ...     node_port=22,
            ...     interface='interface-id',
            ...     service_type='ssh',
            ... )
        """
        ...

    # NOTE: Services are immutable after creation - no update() or patch() methods
    # The Air API does not support PATCH/PUT operations for services
    # To change a service, delete it and create a new one

    def delete(self, *, service: Service | PrimaryKey) -> None:  # type: ignore[override]
        """Delete a service.

        Args:
            service: Service instance or ID

        Example:
            >>> api.services.delete(service='service-id')
            >>> # Or using instance
            >>> api.services.delete(service=service)
        """
        ...
