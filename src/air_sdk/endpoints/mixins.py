# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
import warnings
from http import HTTPStatus
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    TypedDict,
)

from air_sdk.air_json_encoder import AirJSONEncoder
from air_sdk.air_model import DataDict, PrimaryKey, TAirModel_co
from air_sdk.exceptions import AirModelAttributeError
from air_sdk.utils import filter_missing, join_urls, raise_if_invalid_response

if TYPE_CHECKING:
    from air_sdk import AirApi
    from air_sdk.air_model import AirModel


def serialize_payload(data: Dict[str, Any] | List[Dict[str, Any]]) -> str:
    """Serialize the dictionary of values into json using the AirJSONEncoder."""
    return json.dumps(data, indent=None, separators=(',', ':'), cls=AirJSONEncoder)


def build_resource_url(
    base_url: str, resource: AirModel | PrimaryKey, *paths: str
) -> str:
    """Build URL for resource-related endpoints.

    Extracts ID from AirModel object or uses PrimaryKey directly,
    then joins with base URL and additional path segments.

    Args:
        base_url: The base URL for the endpoint
        resource: An AirModel instance or a PrimaryKey (str/UUID)
        *paths: Additional path segments to append

    Returns:
        The constructed URL string

    Example:
        >>> build_resource_url('/api/simulations/', simulation, 'start')
        '/api/simulations/abc-123/start/'
        >>> build_resource_url('/api/nodes/', 'node-id-456', 'interfaces')
        '/api/nodes/node-id-456/interfaces/'
    """
    from air_sdk.air_model import AirModel

    resource_id = resource.id if isinstance(resource, AirModel) else resource
    return join_urls(base_url, str(resource_id), *paths)


class BaseApiMixin:
    """A base class for API Mixins.

    This is primarily used for type hinting.
    """

    __api__: AirApi
    url: str
    load_model: Callable[[DataDict], TAirModel_co]


class PaginatedResponseData(TypedDict):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[DataDict]


class ListApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    """Returns an iterable of model objects.

    Handles pagination in the background.
    """

    def list(self, **params: Any) -> Iterator[TAirModel_co]:
        """Return an iterator of model instances."""
        # Filter out MISSING sentinel values
        params = filter_missing(**params)

        url = self.url
        # Merge default filters with provided params (params take precedence)
        if hasattr(self, 'default_filters') and isinstance(self.default_filters, dict):
            for key, value in self.default_filters.items():
                params.update(self.default_filters)
        # Set up pagination
        next_url = None
        params.setdefault('limit', self.__api__.client.pagination_page_size)
        params = json.loads(
            serialize_payload(params)
        )  # Accounts for UUIDs and AirModel params
        while url or next_url:
            if isinstance(next_url, str):
                response = self.__api__.client.get(next_url)
            else:
                response = self.__api__.client.get(url, params=params)
            raise_if_invalid_response(response)
            paginated_response_data: PaginatedResponseData = response.json()
            url = None  # type: ignore[assignment]
            next_url = paginated_response_data['next']
            for obj_data in paginated_response_data['results']:
                yield self.load_model(obj_data)


class CreateApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    def create(self, *args: Any, **kwargs: Any) -> TAirModel_co:
        # Filter out MISSING sentinel values
        kwargs = filter_missing(**kwargs)
        # Merge default filters with provided params (params take precedence)
        if hasattr(self, 'default_filters') and isinstance(self.default_filters, dict):
            kwargs.update(self.default_filters)
        response = self.__api__.client.post(self.url, data=serialize_payload(kwargs))
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        return self.load_model(response.json())


class GetApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    def get(self, pk: PrimaryKey, **params: Any) -> TAirModel_co:
        detail_url = join_urls(self.url, str(pk))
        response = self.__api__.client.get(detail_url, params=params)
        raise_if_invalid_response(response)
        return self.load_model(response.json())


class PutApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    def put(self, pk: PrimaryKey, **kwargs: Any) -> TAirModel_co:
        # Filter out MISSING sentinel values
        kwargs = filter_missing(**kwargs)
        response = self.__api__.client.put(
            join_urls(self.url, str(pk)), data=serialize_payload(kwargs)
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        try:
            return self.load_model(response.json())
        except AirModelAttributeError:
            # API returned partial response missing required fields
            # Fall back to fetching the full object via GET
            warnings.warn(
                f'PUT response missing required fields for {self.__class__.__name__} '
                f'with pk={pk}, falling back to GET request',
                stacklevel=2,
            )
            return self.get(pk)  # type: ignore[attr-defined,no-any-return]


class PatchApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    def patch(self, pk: PrimaryKey, **kwargs: Any) -> TAirModel_co:
        # Filter out MISSING sentinel values
        kwargs = filter_missing(**kwargs)
        response = self.__api__.client.patch(
            join_urls(self.url, str(pk)), data=serialize_payload(kwargs)
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        try:
            return self.load_model(response.json())
        except AirModelAttributeError:
            # API returned partial response missing required fields
            # Fall back to fetching the full object via GET
            warnings.warn(
                f'PATCH response missing required fields for {self.__class__.__name__} '
                f'with pk={pk}, falling back to GET request',
                stacklevel=2,
            )
            return self.get(pk)  # type: ignore[attr-defined,no-any-return]


class DeleteApiMixin(BaseApiMixin):
    def delete(self, pk: PrimaryKey, **kwargs: Any) -> None:
        """Deletes the instances with the specified primary key."""
        detail_url = join_urls(self.url, str(pk))
        response = self.__api__.client.delete(detail_url, json=kwargs)
        raise_if_invalid_response(
            response, status_code=HTTPStatus.NO_CONTENT, data_type=None
        )
