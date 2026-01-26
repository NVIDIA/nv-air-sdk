# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints import mixins
from air_sdk.endpoints.simulations import Simulation
from air_sdk.utils import raise_if_invalid_response, validate_payload_types

if TYPE_CHECKING:
    from air_sdk.endpoints.simulations import Simulation


@dataclass(eq=False, repr=False)
class ZTPScript(AirModel):
    created: datetime
    modified: datetime
    content: str
    simulation: Simulation = field(metadata=AirModel.FIELD_FOREIGN_KEY)

    def __repr__(self) -> str:
        """Custom repr that truncates content to avoid printing large scripts."""
        # Show first 50 chars of content
        # `textwrap` will collapse newlines
        preview = textwrap.shorten(self.content, width=50, placeholder='...')
        return f'ZTPScript(content={preview!r})'

    @property
    def __pk__(self) -> PrimaryKey:
        return self.simulation.__pk__

    def __refresh__(self, refreshed_obj: ZTPScript | None = None) -> None:  # type: ignore[override]
        if refreshed_obj is None:
            endpoint_api = self.get_model_api()(self.__api__)
            refreshed_obj = endpoint_api.get(simulation=self.simulation)
        self.modified = refreshed_obj.modified
        self.content = refreshed_obj.content

    @classmethod
    def get_model_api(cls) -> type[ZTPScriptEndpointAPI]:
        return ZTPScriptEndpointAPI

    @property
    def model_api(self) -> ZTPScriptEndpointAPI:
        return self.get_model_api()(self.__api__)

    @validate_payload_types
    def update(self, *, content: str, **kwargs: Any) -> None:
        self._ensure_pk_exists('updated')
        updated_obj = self.model_api.patch(
            simulation=self.simulation, content=content, **kwargs
        )
        self.__refresh__(updated_obj)

    def delete(self, **kwargs: Any) -> None:
        self._ensure_pk_exists('deleted')
        self.model_api.delete(simulation=self.simulation, **kwargs)


class ZTPScriptEndpointAPI(BaseEndpointAPI[ZTPScript]):
    API_PATH = 'simulations/{simulation_id}/ztp-script'
    model = ZTPScript

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
    def update(self, *, simulation: Simulation | PrimaryKey, **kwargs: Any) -> ZTPScript:
        return self.patch(simulation=simulation, **kwargs)

    def delete(self, *, simulation: Simulation | PrimaryKey, **kwargs: Any) -> None:
        sim_id = simulation.__pk__ if isinstance(simulation, Simulation) else simulation
        url = self.url.format(simulation_id=str(sim_id))
        response = self.__api__.client.delete(url, json=kwargs)
        raise_if_invalid_response(
            response, status_code=HTTPStatus.NO_CONTENT, data_type=None
        )
        # Clear cached property so next access returns None (only if we have the object)
        if isinstance(simulation, Simulation):
            simulation.clear_cached_property('ztp_script')
