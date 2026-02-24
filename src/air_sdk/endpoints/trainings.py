# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import Any, TypedDict

from air_sdk.air_model import (
    AirModel,
    BaseEndpointAPI,
    PrimaryKey,
)
from air_sdk.endpoints import mixins
from air_sdk.endpoints.simulations import Simulation
from air_sdk.utils import (
    raise_if_invalid_response,
    validate_payload_types,
)


class TrainingNGCData(TypedDict, total=False):
    """External user group data from NGC for a training event."""

    userGroupId: str
    orgName: str
    resourceGroup: str
    name: str
    description: str
    idpListLocked: bool
    requireMatchingEmail: bool
    isUserGroupAdmin: bool
    serviceRoles: list[str]
    companyName: str
    groupContactEmail: str
    permissionSetDesc: str
    startDate: str
    endDate: str
    confirmedUsers: list[str]
    pendingInvitations: list[str]
    type: str


@dataclass(eq=False)
class Training(AirModel):
    id: str = field(repr=False)
    name: str
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    creator: str = field(repr=False)
    org: str = field(repr=False)
    training_simulation: Simulation = field(
        metadata=AirModel.FIELD_FOREIGN_KEY, repr=False
    )
    training_simulation_name: str = field(repr=False)
    training_simulation_state: str = field(repr=False)
    event_time: datetime = field(repr=False)
    ngc_group_id: str = field(repr=False)
    sim_start_time: datetime = field(repr=False)
    sim_end_time: datetime = field(repr=False)
    attendees: list[str] = field(default_factory=list, repr=False)
    workbenches_created: bool = field(default=False, repr=False)

    @classmethod
    def get_model_api(cls) -> type[TrainingEndpointAPI]:
        return TrainingEndpointAPI

    @property
    def model_api(self) -> TrainingEndpointAPI:
        return self.get_model_api()(self.__api__)

    def update(self, **kwargs: Any) -> None:
        self.model_api.update(training=self, **kwargs)

    def add_attendees(self, **kwargs: Any) -> None:
        self.model_api.add_attendees(training=self, **kwargs)

    def remove_attendees(self, **kwargs: Any) -> None:
        self.model_api.remove_attendees(training=self, **kwargs)

    def get_external_user_group(self, **kwargs: Any) -> dict[str, Any]:
        return self.model_api.get_external_user_group(training=self, **kwargs)


class TrainingEndpointAPI(
    mixins.ListApiMixin[Training],
    mixins.CreateApiMixin[Training],
    mixins.GetApiMixin[Training],
    mixins.PatchApiMixin[Training],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Training],
):
    API_PATH = 'trainings'
    ATTENDEES_ADD_PATH = 'attendees/add'
    ATTENDEES_REMOVE_PATH = 'attendees/remove'
    EXTERNAL_USER_GROUP_PATH = 'external-user-group'
    model = Training

    @validate_payload_types
    def update(self, *, training: Training | PrimaryKey, **kwargs: Any) -> Training:
        training_id = training.id if isinstance(training, Training) else training
        result = self.patch(training_id, **kwargs)
        if isinstance(training, Training):
            training.__refresh__(refreshed_obj=result)
        return result

    @validate_payload_types
    def add_attendees(self, *, training: Training | PrimaryKey, **kwargs: Any) -> None:
        url = mixins.build_resource_url(self.url, training, self.ATTENDEES_ADD_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(
            response, data_type=None, status_code=HTTPStatus.NO_CONTENT
        )
        if isinstance(training, Training):
            training.refresh()

    @validate_payload_types
    def remove_attendees(self, *, training: Training | PrimaryKey, **kwargs: Any) -> None:
        url = mixins.build_resource_url(self.url, training, self.ATTENDEES_REMOVE_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(
            response, data_type=None, status_code=HTTPStatus.NO_CONTENT
        )
        if isinstance(training, Training):
            training.refresh()

    @validate_payload_types
    def get_external_user_group(
        self, *, training: Training | PrimaryKey, **kwargs: Any
    ) -> dict[str, Any]:
        url = mixins.build_resource_url(self.url, training, self.EXTERNAL_USER_GROUP_PATH)
        response = self.__api__.client.get(url, params=kwargs)
        raise_if_invalid_response(response)
        response_data: dict[str, Any] = response.json()
        return response_data
