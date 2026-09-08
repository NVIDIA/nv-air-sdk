# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI
from air_sdk.endpoints import mixins


class _OSTemplateRenderFileRequired(TypedDict):
    content: str  # Template body, rendered with the merged vars/generate context


class OSTemplateRenderFile(_OSTemplateRenderFileRequired, total=False):
    owner: str  # POSIX owner, user name or numeric uid. Defaults to `root`
    group: str  # POSIX group, group name or numeric gid. Defaults to `root`
    mode: str  # POSIX octal file mode. Defaults to `0644`


@dataclass(eq=False)
class OSTemplate(AirModel):
    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    os_type: str
    os_template_version: str
    org: str = field(repr=False)
    # Nested payloads stay loose at runtime so a newer air-api can add fields
    # without requiring an SDK upgrade; the stub carries the strict TypedDicts.
    render: dict[str, Any] = field(repr=False)
    creator: Optional[str] = field(default=None, repr=False)
    generate: dict[str, str] = field(default_factory=dict, repr=False)
    vars: list[str] = field(default_factory=list, repr=False)

    @classmethod
    def get_model_api(cls) -> type[OSTemplateEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return OSTemplateEndpointAPI

    @property
    def model_api(self) -> OSTemplateEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)


class OSTemplateEndpointAPI(
    mixins.ListApiMixin[OSTemplate],
    mixins.CreateApiMixin[OSTemplate],
    mixins.GetApiMixin[OSTemplate],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[OSTemplate],
):
    """API client for OS template endpoints."""

    API_PATH = 'manifests/os-templates'
    model = OSTemplate
