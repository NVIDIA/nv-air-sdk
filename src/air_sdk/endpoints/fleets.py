# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import _MISSING_TYPE, MISSING, dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, DataDict
from air_sdk.endpoints import mixins
from air_sdk.utils import validate_payload_types

if TYPE_CHECKING:
    from air_sdk.endpoints.workers import Worker, WorkerEndpointAPI


@dataclass(eq=False)
class Fleet(AirModel):
    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    name: str

    @classmethod
    def get_model_api(cls) -> type[FleetEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model."""
        return FleetEndpointAPI

    @validate_payload_types
    def update(
        self,
        *,
        name: str | _MISSING_TYPE = MISSING,
    ) -> None:
        """Update specific fields of the fleet.


        Example
        -------
            >>> fleet = api.fleets.get('123e4567-e89b-12d3-a456-426614174000')
            >>> fleet.update(name='new-name')
        """
        data = {
            'name': name,
        }
        payload = {key: value for (key, value) in data.items() if value is not MISSING}
        super().update(**payload)

    def create_worker(
        self,
        *,
        fqdn: str,
        ip_address: str,
        cpu_arch: str | _MISSING_TYPE = MISSING,
    ) -> Worker:
        """Create a new worker in the fleet.

        Example
        -------
            >>> fleet = api.fleets.get('123e4567-e89b-12d3-a456-426614174000')
            >>> worker = fleet.create_worker(fqdn='w1.example.com', ip_address='1.1.1.1')
            >>> print(worker)
        """
        return self.__api__.workers.create(
            fleet=self,
            fqdn=fqdn,
            ip_address=ip_address,
            cpu_arch=cpu_arch,
        )

    @property
    def workers(self) -> WorkerEndpointAPI:
        """Query for the related workers of the fleet."""
        from air_sdk.endpoints.workers import WorkerEndpointAPI

        return WorkerEndpointAPI(
            self.__api__, default_filters={'fleet': str(self.__pk__)}
        )


class FleetEndpointAPI(
    mixins.ListApiMixin[Fleet],
    mixins.CreateApiMixin[Fleet],
    mixins.GetApiMixin[Fleet],
    mixins.PatchApiMixin[Fleet],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Fleet],
):
    API_PATH = 'infra/fleets/'
    model = Fleet

    @validate_payload_types
    def list(
        self,
        name: str | _MISSING_TYPE = MISSING,
        search: str | _MISSING_TYPE = MISSING,
        ordering: str | _MISSING_TYPE = MISSING,
        **params: Any,
    ) -> Iterator[Fleet]:
        """List all fleets.

        Example
        -------
            >>> for fleet in api.fleets.list(ordering='name'):
            ...     print(fleet.name)
        """
        params.update(
            {
                k: v
                for k, v in {
                    'name': name,
                    'search': search,
                    'ordering': ordering,
                }.items()
                if v is not MISSING
            }
        )
        return super().list(**params)

    @validate_payload_types
    def create(self, *, name: str) -> Fleet:
        """Create a new fleet.

        Example
        -------
            >>> fleet = api.fleets.create(name='My Fleet')
            >>> print(fleet)
        """
        data: DataDict = {
            'name': name,
        }
        payload = {key: value for (key, value) in data.items() if value is not MISSING}
        return super().create(**payload)
