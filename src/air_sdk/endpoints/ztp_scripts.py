# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import textwrap
from dataclasses import _MISSING_TYPE, MISSING, dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints import mixins
from air_sdk.endpoints.simulations import Simulation
from air_sdk.utils import (
    filter_missing,
    raise_if_invalid_response,
    validate_payload_types,
)

if TYPE_CHECKING:
    from air_sdk.endpoints.simulations import Simulation


@dataclass(eq=False, repr=False)
class ZTPScript(AirModel):
    created: datetime
    modified: datetime
    content: str | None
    ztp_configs: dict[str, Any] | None
    simulation: Simulation = field(metadata=AirModel.FIELD_FOREIGN_KEY)

    def __repr__(self) -> str:
        """Custom repr that lists the OS types and truncates the Cumulus script."""
        if self.ztp_configs:
            os_types = sorted(self.ztp_configs)
        else:
            # Air versions without `ztp_configs` send only the Cumulus script.
            os_types = ['cumulus'] if self.content else []
        # `textwrap` will collapse newlines
        preview = self.content and textwrap.shorten(
            self.content, width=50, placeholder='...'
        )
        return f'ZTPScript(os_types={os_types!r}, content={preview!r})'

    @property
    def __pk__(self) -> PrimaryKey:
        return self.simulation.__pk__

    def __refresh__(self, refreshed_obj: ZTPScript | None = None) -> None:  # type: ignore[override]
        if refreshed_obj is None:
            endpoint_api = self.get_model_api()(self.__api__)
            refreshed_obj = endpoint_api.get(simulation=self.simulation)
        self.modified = refreshed_obj.modified
        self.content = refreshed_obj.content
        self.ztp_configs = refreshed_obj.ztp_configs

    @classmethod
    def get_model_api(cls) -> type[ZTPScriptEndpointAPI]:
        return ZTPScriptEndpointAPI

    @property
    def model_api(self) -> ZTPScriptEndpointAPI:
        return self.get_model_api()(self.__api__)

    def update(self, **kwargs: Any) -> None:
        self._ensure_pk_exists('updated')
        updated_obj = self.model_api.update(simulation=self.simulation, **kwargs)
        self.__refresh__(updated_obj)

    def delete(self) -> None:
        self._ensure_pk_exists('deleted')
        self.model_api.delete(simulation=self.simulation)


class ZTPScriptEndpointAPI(BaseEndpointAPI[ZTPScript]):
    API_PATH = 'simulations/{simulation_id}/ztp-script'
    model = ZTPScript

    @validate_payload_types
    def create(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        content: str | _MISSING_TYPE = MISSING,
        ztp_configs: dict[str, Any] | _MISSING_TYPE = MISSING,
        **kwargs: Any,
    ) -> ZTPScript:
        sim_id = simulation.__pk__ if isinstance(simulation, Simulation) else simulation
        url = self.url.format(simulation_id=str(sim_id))
        payload = filter_missing(content=content, ztp_configs=ztp_configs, **kwargs)
        response = self.__api__.client.post(url, data=mixins.serialize_payload(payload))
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        if isinstance(simulation, Simulation):
            # Clear cached property so next access returns the new configuration
            simulation.clear_cached_property('ztp_script')
        else:
            # With only an ID, get the full simulation object for the model
            simulation = self.__api__.simulations.get(simulation)
        return self.load_model(response.json() | {'simulation': simulation})

    def get(self, *, simulation: Simulation | PrimaryKey) -> ZTPScript:
        sim_id = simulation.__pk__ if isinstance(simulation, Simulation) else simulation
        url = self.url.format(simulation_id=str(sim_id))
        response = self.__api__.client.get(url)
        raise_if_invalid_response(response)
        # If we only have an ID, we need to get the full simulation object for the model
        if not isinstance(simulation, Simulation):
            simulation = self.__api__.simulations.get(simulation)
        return self.load_model(response.json() | {'simulation': simulation})

    def patch(self, *, simulation: Simulation | PrimaryKey, **kwargs: Any) -> ZTPScript:
        sim_id = simulation.__pk__ if isinstance(simulation, Simulation) else simulation
        url = self.url.format(simulation_id=str(sim_id))
        payload = mixins.serialize_payload(kwargs)
        response = self.__api__.client.patch(url, data=payload)
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        # If we only have an ID, we need to get the full simulation object for the model
        if not isinstance(simulation, Simulation):
            simulation = self.__api__.simulations.get(simulation)
        return self.load_model(response.json() | {'simulation': simulation})

    @validate_payload_types
    def update(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        content: str | _MISSING_TYPE = MISSING,
        ztp_configs: dict[str, Any] | _MISSING_TYPE = MISSING,
        **kwargs: Any,
    ) -> ZTPScript:
        return self.patch(
            simulation=simulation,
            **filter_missing(content=content, ztp_configs=ztp_configs, **kwargs),
        )

    def delete(self, *, simulation: Simulation | PrimaryKey) -> None:
        sim_id = simulation.__pk__ if isinstance(simulation, Simulation) else simulation
        url = self.url.format(simulation_id=str(sim_id))
        response = self.__api__.client.delete(url)
        raise_if_invalid_response(
            response, status_code=HTTPStatus.NO_CONTENT, data_type=None
        )
        # Clear cached property so next access returns None (only if we have the object)
        if isinstance(simulation, Simulation):
            simulation.clear_cached_property('ztp_script')
