# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints import mixins


@dataclass(eq=False)
class History(AirModel):
    object_id: str
    model: str
    created: datetime = field(repr=False)
    actor: str
    description: str
    category: str

    @classmethod
    def get_model_api(cls) -> type[HistoryEndpointAPI]:
        return HistoryEndpointAPI

    def refresh(self) -> None:
        raise NotImplementedError('History entries are immutable and cannot be refreshed')

    @property
    def __pk__(self) -> PrimaryKey:
        return f'{self.model}:{self.object_id}'


class HistoryEndpointAPI(mixins.ListApiMixin[History], BaseEndpointAPI[History]):
    API_PATH = 'histories'
    model = History
