# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from air_sdk.air_model import (
    AirModel,
    BaseEndpointAPI,
)
from air_sdk.bc.base import BaseCompatMixin
from air_sdk.endpoints import mixins


@dataclass(eq=False)
class SSHKey(BaseCompatMixin, AirModel):
    id: str = field(repr=False)
    created: datetime = field(repr=False)
    name: str
    fingerprint: str

    @classmethod
    def get_model_api(cls) -> type[SSHKeyEndpointAPI]:
        return SSHKeyEndpointAPI


class SSHKeyEndpointAPI(
    mixins.ListApiMixin[SSHKey],
    mixins.CreateApiMixin[SSHKey],
    mixins.GetApiMixin[SSHKey],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[SSHKey],
):
    API_PATH = 'users/ssh-keys/'
    model = SSHKey
