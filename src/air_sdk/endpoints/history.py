# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterator, cast

from air_sdk.air_model import AirModel, BaseEndpointAPI, DataDict, PrimaryKey
from air_sdk.endpoints import mixins
from air_sdk.types import HistoryEntry, HistoryFilters
from air_sdk.utils import (
    filter_missing,
    iso_string_to_datetime,
    join_urls,
    raise_if_invalid_response,
)

if TYPE_CHECKING:
    from air_sdk import AirApi


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


def _to_history_entry(data: DataDict) -> HistoryEntry:
    """Turn a nested history payload into a `HistoryEntry`, parsing `created`."""
    entry = dict(data)
    created = entry.get('created')
    if isinstance(created, str):
        entry['created'] = iso_string_to_datetime(created)
    return cast(HistoryEntry, entry)


class HistoryModelMixin:
    """Nested history reads for a resource (`history` + `history-filters`).

    Mixed into resource models (`Simulation`, `Node`, `Image`, `MarketplaceDemo`)
    whose viewsets expose the nested `GET .../<id>/history/` and
    `GET .../<id>/history-filters/` actions. History entries are read-only,
    immutable value shapes, so these return plain `HistoryEntry` dicts rather
    than models (see `response_handling`).
    """

    if TYPE_CHECKING:
        __api__: AirApi

        @property
        def detail_url(self) -> str: ...

    def list_history(self, **kwargs: Any) -> Iterator[HistoryEntry]:
        """Yield the resource's history entries from its nested endpoint."""
        histories = self.__api__.histories
        url = join_urls(self.detail_url, 'history')
        params = filter_missing(**kwargs)
        params.setdefault('limit', self.__api__.client.pagination_page_size)
        # Serialize to normalize UUIDs/AirModel params, matching ListApiMixin.list.
        params = json.loads(mixins.serialize_payload(params))
        return histories._paginate(url, params, _to_history_entry)

    def get_history_filters(self) -> HistoryFilters:
        """Return the distinct history filter values for the resource."""
        url = join_urls(self.detail_url, 'history-filters')
        response = self.__api__.client.get(url)
        raise_if_invalid_response(response)
        return cast(HistoryFilters, response.json())


class HistoryEndpointAPI(mixins.ListApiMixin[History], BaseEndpointAPI[History]):
    API_PATH = 'histories'
    model = History
