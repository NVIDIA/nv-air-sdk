# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from air_sdk.air_model import AirModel, BaseEndpointAPI
from air_sdk.endpoints import mixins
from air_sdk.endpoints.images import Image


@dataclass(eq=False)
class OSImageManifest(AirModel):
    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    image: Image = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    os_type: str
    # Nested payloads stay loose at runtime so a newer air-api can add fields
    # without requiring an SDK upgrade; the stub carries the strict TypedDicts.
    platforms: dict[str, Any] = field(repr=False)
    capabilities: dict[str, Any] = field(repr=False)
    os_template_partition: Optional[str] = field(default=None, repr=False)
    creator: Optional[str] = field(default=None, repr=False)

    @classmethod
    def get_model_api(cls) -> type[OSImageManifestEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return OSImageManifestEndpointAPI

    @property
    def model_api(self) -> OSImageManifestEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)


class OSImageManifestEndpointAPI(
    mixins.ListApiMixin[OSImageManifest],
    mixins.CreateApiMixin[OSImageManifest],
    mixins.GetApiMixin[OSImageManifest],
    mixins.PatchApiMixin[OSImageManifest],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[OSImageManifest],
):
    """API client for OS image manifest endpoints."""

    API_PATH = 'manifests/os-images'
    model = OSImageManifest
