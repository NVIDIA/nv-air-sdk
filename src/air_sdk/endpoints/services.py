# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from air_sdk.air_model import AirModel, BaseEndpointAPI
from air_sdk.bc import BaseCompatMixin, ServiceCompatMixin, ServiceEndpointAPICompatMixin
from air_sdk.endpoints import mixins
from air_sdk.endpoints.interfaces import Interface


@dataclass(eq=False)
class Service(ServiceCompatMixin, BaseCompatMixin, AirModel):
    id: str
    name: str
    node_port: int
    service_type: str
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    interface: Interface = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    worker_port: int | None = field(default=None, repr=False)
    worker_fqdn: str | None = field(default=None, repr=False)

    @classmethod
    def get_model_api(cls) -> type[ServiceEndpointAPI]:
        return ServiceEndpointAPI

    @property
    def model_api(self) -> ServiceEndpointAPI:
        return self.get_model_api()(self.__api__)


class ServiceEndpointAPI(
    ServiceEndpointAPICompatMixin,
    mixins.ListApiMixin[Service],
    mixins.CreateApiMixin[Service],
    mixins.GetApiMixin[Service],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Service],
):
    API_PATH = 'simulations/nodes/interfaces/services/'
    model = Service

    # NOTE: Services are immutable after creation - delete and recreate to change
    # The Air API does not support PATCH/PUT (update operations)
