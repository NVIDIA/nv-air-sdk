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
class Manifest(BaseCompatMixin, ManifestCompatMixin, AirModel):
    id: str
    org_name: str
    docker_run_parameters: dict[str, Any] = field(repr=False)
    emulation_type: str = field(repr=False)
    platform_information: dict[str, Any] = field(repr=False)
    simulator_image: Image = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    simulator_resources: dict[str, Any] = field(repr=False)
    artifacts_directory: Optional[str] = field(default=None, repr=False)
    artifacts_directory_max_size_gb: Optional[int] = field(default=None, repr=False)
    boot_group: Optional[int] = field(default=None, repr=False)
    configure_node_properties: Optional[dict[str, Any]] = field(default=None, repr=False)
    configure_simulator: Optional[dict[str, Any]] = field(default=None, repr=False)
    simulation_engine_versions: Optional[list[str]] = field(default=None, repr=False)
    emulation_params: Optional[dict[str, Any]] = field(default=None, repr=False)
    port_mapping_required: Optional[bool] = field(default=None, repr=False)

    @classmethod
    def get_model_api(cls) -> type[ManifestEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return ManifestEndpointAPI

    @property
    def model_api(self) -> ManifestEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)


class ManifestEndpointAPI(
    ManifestEndpointAPICompatMixin,
    mixins.ListApiMixin[Manifest],
    mixins.CreateApiMixin[Manifest],
    mixins.GetApiMixin[Manifest],
    mixins.PatchApiMixin[Manifest],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Manifest],
):
    """API client for manifest endpoints."""

    API_PATH = 'manifests'
    model = Manifest
