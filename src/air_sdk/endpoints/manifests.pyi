# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for manifests endpoint type hints.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, List

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc import BaseCompatMixin
from air_sdk.bc.manifests import ManifestCompatMixin
from air_sdk.endpoints.images import Image
from air_sdk.types import (
    DockerRunParameters,
    EmulationParams,
    Platform,
    Resources,
)

@dataclass(eq=False)
class Manifest(BaseCompatMixin, ManifestCompatMixin, AirModel):
    """Manifest model representing a simulator/platform configuration.

    Manifests define how a specific network device or platform should be
    emulated, including resource requirements, docker parameters, and
    platform capabilities.

    Attributes:
        id: Unique identifier for the manifest (required)
        org_name: Organization name that owns this manifest (read-only, set by API)
        docker_run_parameters: Docker container runtime parameters (required)
        emulation_type: Type of emulation (required)
        platform_information: Dictionary of platform configurations (required)
        simulator_image: Docker image used for the simulator (required)
        simulator_resources: Resource requirements for the simulator (required)
        description: Manifest description (optional)
        artifacts_directory: Directory path for simulator artifacts (optional)
        artifacts_directory_max_size_gb: Maximum size for artifacts dir in GB (optional)
        boot_group: Boot group number for startup ordering (optional)
        configure_node_properties: Node configuration properties (optional)
        configure_simulator: Simulator configuration parameters (optional)
        simulation_engine_versions: List of supported sim engine versions (optional)
        emulation_params: Emulation-specific parameters (optional)
        port_mapping_required: Whether port mapping is required (optional, read-only)
    """

    id: str
    org_name: str
    docker_run_parameters: dict[str, Any]
    emulation_type: str
    platform_information: dict[str, Any]
    simulator_image: Image
    simulator_resources: dict[str, Any]
    description: str | None
    artifacts_directory: str | None
    artifacts_directory_max_size_gb: int | None
    boot_group: int | None
    configure_node_properties: dict[str, Any] | None
    configure_simulator: dict[str, Any] | None
    simulation_engine_versions: list[str] | None
    emulation_params: dict[str, Any] | None
    port_mapping_required: bool | None

    @classmethod
    def get_model_api(cls) -> type[ManifestEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model.

        Returns:
            ManifestEndpointAPI class
        """
        ...

    @property
    def model_api(self) -> ManifestEndpointAPI:
        """The current model API instance.

        Returns:
            ManifestEndpointAPI instance
        """
        ...

    def update(
        self,
        *,
        docker_run_parameters: DockerRunParameters | dict[str, Any] = ...,
        emulation_type: str = ...,
        platform_information: dict[str, Platform | dict[str, Any]] = ...,
        simulator_image: Image | str = ...,
        simulator_resources: Resources | dict[str, Any] = ...,
        description: str = ...,
        artifacts_directory: str = ...,
        artifacts_directory_max_size_gb: int = ...,
        boot_group: int = ...,
        configure_node_properties: dict[str, Any] = ...,
        configure_simulator: dict[str, Any] = ...,
        simulation_engine_versions: list[str] = ...,
        emulation_params: EmulationParams | dict[str, Any] = ...,
    ) -> None:
        """Update the manifest's properties.

        Args:
            docker_run_parameters: Docker runtime parameters
            emulation_type: Type of emulation
            platform_information: Platform configurations
            simulator_image: Docker image for the simulator
            simulator_resources: Resource requirements
            description: Manifest description
            artifacts_directory: Directory path for simulator artifacts
            artifacts_directory_max_size_gb: Max size for artifacts dir
            boot_group: Boot group number
            configure_node_properties: Node configuration properties
            configure_simulator: Simulator configuration
            simulation_engine_versions: Supported engine versions
            emulation_params: Emulation parameters

        Example:
            >>> manifest.update(boot_group=2)
            >>> manifest.update(description='Updated manifest')
        """
        ...

    def delete(self) -> None:
        """Delete this manifest.

        Example:
            >>> manifest = api.manifests.get('manifest-id-123')
            >>> manifest.delete()
        """
        ...

class ManifestEndpointAPI(BaseEndpointAPI[Manifest]):
    """API client for manifest endpoints."""

    API_PATH: str
    model: type[Manifest]

    def list(
        self,
        *,
        id: str = ...,
        org_name: str = ...,
        emulation_type: str = ...,
        port_mapping_required: bool = ...,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
        **params: Any,
    ) -> Iterator[Manifest]:
        """List all manifests with optional filtering.

        Args:
            id: Filter by manifest ID
            org_name: Filter by organization name
            emulation_type: Filter by emulation type
            port_mapping_required: Filter by port mapping requirement (V2 BC field)
            limit: Number of results to return per page
            offset: The initial index from which to return the results
            ordering: Order objects by field. Prefix with "-" for desc order
            search: Search term to filter manifests
            **params: Additional query parameters

        Returns:
            Iterator of Manifest instances

        Example:
            >>> # List all manifests
            >>> for manifest in api.manifests.list():
            ...     print(manifest.emulation_type)

            >>> # Filter by emulation type
            >>> for manifest in api.manifests.list(emulation_type='NIC_INFINIBAND'):
                ...     print(manifest.org_name)

            >>> # Search and order
            >>> for manifest in api.manifests.list(search='cumulus', ordering='-created'):
            ...     print(manifest.id)
        """
        ...

    def create(
        self,
        *,
        docker_run_parameters: DockerRunParameters | dict[str, Any],
        emulation_type: str,
        platform_information: dict[str, Platform | dict[str, Any]],
        simulator_image: Image | str,
        simulator_resources: Resources | dict[str, Any],
        description: str = ...,
        artifacts_directory: str = ...,
        artifacts_directory_max_size_gb: int = ...,
        boot_group: int = ...,
        configure_node_properties: dict[str, Any] = ...,
        configure_simulator: dict[str, Any] = ...,
        simulation_engine_versions: List[str] = ...,
        emulation_params: EmulationParams | dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Manifest:
        """Create a new manifest.

        Note: org_name is automatically determined by API and cannot be specified.

        Args:
            docker_run_parameters: Docker runtime parameters (required)
            emulation_type: Type of emulation (required)
            platform_information: Platform configurations (required)
            simulator_image: Docker image for the simulator - Image obj or ID (required)
            simulator_resources: Resource requirements (required)
            description: Manifest description (optional)
            artifacts_directory: Directory path for simulator artifacts (optional)
            artifacts_directory_max_size_gb: Max size for artifacts dir (optional)
            boot_group: Boot group number (optional)
            configure_node_properties: Node configuration properties (optional)
            configure_simulator: Simulator configuration (optional)
            simulation_engine_versions: Supported engine versions (optional)
            emulation_params: Emulation parameters (optional)
            **kwargs: Additional fields

        Returns:
            The created Manifest instance

        Example:
            >>> manifest = api.manifests.create(
            ...     artifacts_directory='/artifacts',
            ...     artifacts_directory_max_size_gb=10,
            ...     boot_group=1,
            ...     configure_node_properties={},
            ...     configure_simulator={},
            ...     docker_run_parameters={
            ...         'tmpfs': [],
            ...         'cap_add': ['NET_ADMIN'],
            ...         'devices': ['/dev/kvm'],
            ...         'volumes': [],
            ...         'environment': {},
            ...     },
            ...     emulation_type='NIC_INFINIBAND',
            ...     platform_information={},
            ...     simulation_engine_versions=['1.0'],
            ...     simulator_image='image-id',
            ...     simulator_resources={'cpu': 2.0, 'memory': 4096},
            ...     emulation_params={
            ...         'direct_link_emulation': True,
            ...         'max_network_pci': 8,
            ...     },
            ... )
        """
        ...

    def get(self, pk: PrimaryKey) -> Manifest:
        """Get a specific manifest by ID.

        Args:
            pk: The manifest ID (string or UUID)

        Returns:
            The Manifest instance

        Example:
            >>> manifest = api.manifests.get('manifest-id-123')
            >>> print(manifest.emulation_type)
        """
        ...

    def patch(
        self,
        pk: PrimaryKey,
        *,
        docker_run_parameters: DockerRunParameters | dict[str, Any] = ...,
        emulation_type: str = ...,
        platform_information: dict[str, Platform | dict[str, Any]] = ...,
        simulator_image: Image | str = ...,
        simulator_resources: Resources | dict[str, Any] = ...,
        description: str = ...,
        artifacts_directory: str = ...,
        artifacts_directory_max_size_gb: int = ...,
        boot_group: int = ...,
        configure_node_properties: dict[str, Any] = ...,
        configure_simulator: dict[str, Any] = ...,
        simulation_engine_versions: List[str] = ...,
        emulation_params: EmulationParams | dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Manifest:
        """Update a manifest's properties.

        Args:
            pk: The manifest ID (string or UUID)
            docker_run_parameters: Docker runtime parameters
            emulation_type: Type of emulation
            platform_information: Platform configurations
            simulator_image: Docker image for the simulator
            simulator_resources: Resource requirements
            description: Manifest description
            artifacts_directory: Directory path for simulator artifacts
            artifacts_directory_max_size_gb: Max size for artifacts dir
            boot_group: Boot group number
            configure_node_properties: Node configuration properties
            configure_simulator: Simulator configuration
            simulation_engine_versions: Supported engine versions
            emulation_params: Emulation parameters
            **kwargs: Additional fields to update

        Returns:
            The updated Manifest instance

        Example:
            >>> updated_manifest = api.manifests.patch(
            ...     pk='manifest-id-123',
            ...     boot_group=2,
            ... )
        """
        ...

    def delete(self, pk: PrimaryKey, **kwargs: Any) -> None:
        """Delete a manifest.

        Args:
            pk: The manifest ID (string or UUID) to delete
            **kwargs: Additional parameters

        Example:
            >>> api.manifests.delete('manifest-id-123')
        """
        ...
