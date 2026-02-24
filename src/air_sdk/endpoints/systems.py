# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from air_sdk.air_model import AirModel, BaseEndpointAPI
from air_sdk.bc import BaseCompatMixin
from air_sdk.endpoints import mixins
from air_sdk.endpoints.images import Image
from air_sdk.endpoints.simulations import Simulation

if TYPE_CHECKING:
    from air_sdk.endpoints import Image, Simulation


@dataclass(eq=False)
class System(BaseCompatMixin, AirModel):
    """System model representing a system in the AIR platform."""

    id: str
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    name: str
    simulation: Simulation | None = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    image: Image = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    memory: int = field(repr=False)
    storage: int = field(repr=False)
    cpu: int = field(repr=False)
    category: str = field(repr=False)
    attributes: dict[str, Any] = field(repr=False)
    split_options: list[int] | None = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type[SystemEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return SystemEndpointAPI

    @property
    def model_api(self) -> SystemEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)


class SystemEndpointAPI(
    mixins.ListApiMixin[System],
    mixins.GetApiMixin[System],
    BaseEndpointAPI[System],
):
    """Endpoint API for System operations."""

    API_PATH = 'systems/nodes'
    model = System
