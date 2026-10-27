# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
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
class ZTPTemplate(AirModel):
    id: str = field(repr=False)
    os_type: str
    template: str | dict[str, Any] = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    created_by: str | None = field(repr=False)
    last_modified_by: str | None = field(repr=False)

    @property
    def primary_key_field(self) -> str:
        return 'os_type'

    def __setattr__(self, name: str, value: Any) -> None:
        # `os_type` is the primary key: changing it would point this object at
        # the other OS type's template.
        if name == 'os_type' and value != getattr(self, 'os_type', value):
            raise AttributeError(
                '`os_type` identifies the template and cannot be changed; '
                'create a template for the other OS type instead.'
            )
        super().__setattr__(name, value)

    @classmethod
    def get_model_api(cls) -> type[ZTPTemplateEndpointAPI]:
        return ZTPTemplateEndpointAPI

    @property
    def model_api(self) -> ZTPTemplateEndpointAPI:
        return self.get_model_api()(self.__api__)

    def update(self, **kwargs: Any) -> None:
        self._ensure_pk_exists('updated')
        self.model_api.update(ztp_template=self, **kwargs)


class ZTPTemplateEndpointAPI(
    mixins.GetApiMixin[ZTPTemplate],
    mixins.CreateApiMixin[ZTPTemplate],
    mixins.PatchApiMixin[ZTPTemplate],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[ZTPTemplate],
):
    API_PATH = 'manifests/ztp-templates'
    model = ZTPTemplate

    @validate_payload_types
    def update(
        self, *, ztp_template: ZTPTemplate | PrimaryKey, **kwargs: Any
    ) -> ZTPTemplate:
        os_type = (
            ztp_template.os_type
            if isinstance(ztp_template, ZTPTemplate)
            else ztp_template
        )
        result = self.patch(os_type, **kwargs)
        if isinstance(ztp_template, ZTPTemplate):
            ztp_template.__refresh__(refreshed_obj=result)
        return result
