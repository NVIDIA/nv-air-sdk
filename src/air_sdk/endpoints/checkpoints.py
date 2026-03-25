# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from air_sdk.air_model import (
    AirModel,
    BaseEndpointAPI,
    PrimaryKey,
)
from air_sdk.endpoints import mixins
from air_sdk.utils import validate_payload_types


@dataclass(eq=False)
class Checkpoint(AirModel):
    id: str = field(repr=False)
    name: str
    favorite: bool
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    run: str = field(repr=False)
    state: str = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type[CheckpointEndpointAPI]:
        return CheckpointEndpointAPI

    @property
    def model_api(self) -> CheckpointEndpointAPI:
        return self.get_model_api()(self.__api__)

    def update(self, **kwargs: Any) -> None:
        self.model_api.update(checkpoint=self, **kwargs)


class CheckpointEndpointAPI(
    mixins.ListApiMixin[Checkpoint],
    mixins.GetApiMixin[Checkpoint],
    mixins.PatchApiMixin[Checkpoint],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Checkpoint],
):
    API_PATH = 'simulations/runs/checkpoints'
    model = Checkpoint

    @validate_payload_types
    def update(self, *, checkpoint: Checkpoint | PrimaryKey, **kwargs: Any) -> Checkpoint:
        checkpoint_id = (
            checkpoint.id if isinstance(checkpoint, Checkpoint) else checkpoint
        )
        result = self.patch(checkpoint_id, **kwargs)
        if isinstance(checkpoint, Checkpoint):
            checkpoint.__refresh__(refreshed_obj=result)
        return result
