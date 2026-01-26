# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from air_sdk.air_model import AirModel, BaseEndpointAPI
from air_sdk.bc import OrganizationCompatMixin, OrganizationEndpointAPICompatMixin
from air_sdk.endpoints import mixins
from air_sdk.types import ResourceBudgetUsage


@dataclass(eq=False)
class Organization(OrganizationCompatMixin, AirModel):
    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    org_display_name: str
    org_nca_id: str = field(repr=False)
    cpu: int | float = field(repr=False)
    memory: int | float = field(repr=False)
    disk_storage_total: int | float = field(repr=False)
    disk_storage_per_node: int = field(repr=False)
    image_storage: int = field(repr=False)
    userconfigs: int = field(repr=False)
    usage: ResourceBudgetUsage = field(repr=False)

    @property
    def name(self) -> str:
        return self.org_display_name

    @classmethod
    def get_model_api(cls) -> type[OrganizationEndpointAPI]:
        return OrganizationEndpointAPI

    @property
    def model_api(self) -> OrganizationEndpointAPI:
        return self.get_model_api()(self.__api__)

    # Methods no longer supported in the new API
    def add_member(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError('Organization.add_member() is no longer supported')

    def add_members(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError('Organization.add_members() is no longer supported')

    def remove_member(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError('Organization.remove_member() is no longer supported')

    def remove_members(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError('Organization.remove_members() is no longer supported')

    def create_fleet(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError('Organization.create_fleet() is no longer supported')

    def list_members(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError('Organization.list_members() is no longer supported')


class OrganizationEndpointAPI(
    OrganizationEndpointAPICompatMixin,
    mixins.ListApiMixin[Organization],
    mixins.GetApiMixin[Organization],
    BaseEndpointAPI[Organization],
):
    API_PATH = 'resource-budgets'
    model = Organization

    # Method no longer supported in the new API
    def create(self, *args: Any, **kwargs: Any) -> Organization:
        raise NotImplementedError('Organization creation is no longer supported')
