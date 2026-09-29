# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from air_sdk.air_model import AirModel, BaseEndpointAPI
from air_sdk.bc import (
    BaseCompatMixin,
    ManifestCompatMixin,
    ManifestEndpointAPICompatMixin,
)
from air_sdk.endpoints import mixins
from air_sdk.endpoints.images import Image


@dataclass(eq=False)
class PluginImageManifest(BaseCompatMixin, ManifestCompatMixin, AirModel):
    # Read-only in v3: set by API (e.g. from NGC)
    _READ_ONLY_FIELDS = ['org_name']

    id: str
    org_name: str
    docker_run_parameters: dict[str, Any] = field(repr=False)
    emulation_type: str = field(repr=False)
    platform_information: dict[str, Any] = field(repr=False)
    simulator_image: Image = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    simulator_resources: dict[str, Any] = field(repr=False)
    artifacts_directory: Optional[str] = field(default=None, repr=False)
    artifacts_directory_max_size_gb: Optional[float] = field(default=None, repr=False)
    boot_group: Optional[int] = field(default=None, repr=False)
    configure_node_properties: Optional[dict[str, Any]] = field(default=None, repr=False)
    configure_simulator: Optional[dict[str, Any]] = field(default=None, repr=False)
    simulation_engine_versions: Optional[list[str]] = field(default=None, repr=False)
    emulation_params: Optional[dict[str, Any]] = field(default=None, repr=False)
    port_mapping_required: Optional[bool] = field(default=None, repr=False)
    secrets: Optional[list[dict[str, Any]]] = field(default=None, repr=False)

    @classmethod
    def get_model_api(cls) -> type[PluginImageManifestEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return PluginImageManifestEndpointAPI

    @property
    def model_api(self) -> PluginImageManifestEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)


class PluginImageManifestEndpointAPI(
    ManifestEndpointAPICompatMixin,
    mixins.ListApiMixin[PluginImageManifest],
    mixins.CreateApiMixin[PluginImageManifest],
    mixins.GetApiMixin[PluginImageManifest],
    mixins.PatchApiMixin[PluginImageManifest],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[PluginImageManifest],
):
    """API client for plugin image manifest endpoints."""

    API_PATH = 'manifests/plugin-images'
    model = PluginImageManifest
