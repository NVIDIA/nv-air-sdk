# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI
from air_sdk.endpoints import mixins


class PlatformInformationPortMapEntry(TypedDict):
    asic: str  # The ASIC this entry applies to
    label_port: str  # The label port for the given ASIC
    local_port: str  # The local port for the given ASIC
    split_num: str  # The split number for the given ASIC


#: Port map layout: split factor (`'1'`, `'2'`, ... or `'mgmt'`) -> interface name
#: -> entry.
PlatformInformationPortMap = dict[str, dict[str, PlatformInformationPortMapEntry]]


class MinimumResources(TypedDict):
    cpu: int  # Number of CPU cores
    memory: int  # Memory, in MiB
    storage: int  # Storage, in GiB


class PortsConfig(TypedDict):
    num_label_ports: int  # Number of label ports on the platform
    default_split: str  # Default split factor per label port (`'1'` = un-split)
    split_options: list[str]  # Permitted split factors


@dataclass(eq=False)
class PlatformInformation(AirModel):
    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    model: str
    platform_information_version: str
    # Nested payloads stay loose at runtime so a newer air-api can add fields
    # without requiring an SDK upgrade; the stub carries the strict TypedDicts.
    port_map: dict[str, Any] = field(repr=False)
    ports_config: dict[str, Any] = field(repr=False)
    os_type: Optional[str]
    emulation_type: Optional[str]
    creator: Optional[str] = field(default=None, repr=False)
    vars: dict[str, Any] = field(default_factory=dict, repr=False)
    simulator_config: dict[str, Any] = field(default_factory=dict, repr=False)
    minimum_resources: Optional[dict[str, Any]] = field(default=None, repr=False)

    @classmethod
    def get_model_api(cls) -> type[PlatformInformationEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return PlatformInformationEndpointAPI

    @property
    def model_api(self) -> PlatformInformationEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)


class PlatformInformationEndpointAPI(
    mixins.ListApiMixin[PlatformInformation],
    mixins.CreateApiMixin[PlatformInformation],
    mixins.GetApiMixin[PlatformInformation],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[PlatformInformation],
):
    """API client for platform information endpoints."""

    API_PATH = 'manifests/platform-information'
    model = PlatformInformation
