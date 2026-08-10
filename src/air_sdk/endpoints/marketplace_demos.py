# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import Any

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc import (
    BaseCompatMixin,
    BaseEndpointAPICompatMixin,
    MarketplaceDemoCompatMixin,
    MarketplaceDemoEndpointAPICompatMixin,
)
from air_sdk.endpoints import mixins

# Import Simulation at runtime (not just TYPE_CHECKING) because get_type_hints() needs it
from air_sdk.endpoints.simulations import Simulation
from air_sdk.types import SimRequiredResources
from air_sdk.utils import join_urls, raise_if_invalid_response, validate_payload_types


@dataclass(eq=False)
class MarketplaceDemo(BaseCompatMixin, MarketplaceDemoCompatMixin, AirModel):
    """Marketplace demo model representing a marketplace demo.

    Attributes:
        id: Unique identifier for the marketplace demo
        name: Human-readable name of the marketplace demo
        created: Timestamp when the marketplace demo was created
        modified: Timestamp when the marketplace demo was last modified
        creator: The creator of the marketplace demo
        description: The description of the demo
        demo_simulation_state: The state of the simulation instance associated with
            this demo which acts as the template for all provisioned simulations from
            this demo.
        documentation: The documentation of the marketplace demo
        repo: The repository of the marketplace demo
        tags: The tags of the marketplace demo
        published: Whether the marketplace demo is published
        publicly_published: Whether a published demo is publicly accessible
        icon: The icon of the marketplace demo
        demo: Demo simulation to be used as a base for cloned simulations.
        publish_access_record_id: The active publish access record ID, if any
        featured: Whether the marketplace demo is featured. Featured demos appear
            before non-featured demos in the default ordering.
        order: The ordering value of the marketplace demo. Demos with a lower
            ``order`` value appear before demos with a higher ``order`` value. May
            be null.
        provision_count: Number of times a clone has been provisioned from this
            marketplace demo (counted when the provision request creates the clone;
            not decremented if that clone later fails to boot).
    """

    id: str
    name: str
    demo: Simulation = field(metadata=AirModel.FIELD_FOREIGN_KEY)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    creator: str = field(repr=False)
    documentation: str | None = field(repr=False)
    tags: list[str] = field(repr=False)
    published: bool = field(repr=False)
    publicly_published: bool = field(repr=False)
    demo_simulation_state: str = field(repr=False)
    expected_resource_usage: SimRequiredResources = field(repr=False)
    description: str | None
    repo: str | None
    publisher: str = field(repr=False)
    icon: str | None
    publish_access_record_id: str | None = field(repr=False)
    featured: bool = field(repr=False)
    order: int | None = field(repr=False)
    provision_count: int = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type[MarketplaceDemoEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return MarketplaceDemoEndpointAPI

    @property
    def model_api(self) -> MarketplaceDemoEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    def publish(self, **kwargs: Any) -> None:
        """Publish the marketplace demo.

        A ``publisher`` must be set on the demo before it can be published.

        Example:
            >>> marketplace_demo.publish()
        """
        self.model_api.publish(marketplace_demo=self, **kwargs)

    def unpublish(self, **kwargs: Any) -> None:
        """Immediately unpublish the marketplace demo (privileged).

        This privileged action takes no request body. To submit a gated unpublish
        request for review instead, use :meth:`request_unpublish`.

        Example:
            >>> marketplace_demo.unpublish()
        """
        self.model_api.unpublish(marketplace_demo=self, **kwargs)

    def request_publish(self, **kwargs: Any) -> MarketplaceDemo:
        """Submit a request to publish this marketplace demo.

        A ``publisher`` must be set on the demo — either previously or via this
        request (pass ``publisher=...``) — before it can be queued for publishing.

        Example:
            >>> marketplace_demo.request_publish(justification='Ready for community use')
        """
        return self.model_api.request_publish(marketplace_demo=self, **kwargs)

    def request_unpublish(self, **kwargs: Any) -> MarketplaceDemo:
        """Submit a request to unpublish this marketplace demo.

        Example:
            >>> marketplace_demo.request_unpublish(justification='No longer maintained')
        """
        return self.model_api.request_unpublish(marketplace_demo=self, **kwargs)

    def request_public(self, **kwargs: Any) -> MarketplaceDemo:
        """Submit a request to change marketplace demo visibility to public or restricted.

        Example:
            >>> marketplace_demo.request_public(
            ...     prefer_public=True,
            ...     justification='Open source',
            ...     publish_images=True,
            ... )
        """
        return self.model_api.request_public(marketplace_demo=self, **kwargs)

    def request_allowlist_change(self, **kwargs: Any) -> MarketplaceDemo:
        """Submit a request to change the allowlist for this marketplace demo.

        Example:
            >>> marketplace_demo.request_allowlist_change(
            ...     justification='Add partner orgs',
            ...     allowed_orgs_request_text='org-a, org-b',
            ... )
        """
        return self.model_api.request_allowlist_change(marketplace_demo=self, **kwargs)

    def cancel_publish_access_record(self, **kwargs: Any) -> MarketplaceDemo:
        """Cancel the active publish access record for this marketplace demo.

        Example:
            >>> marketplace_demo.cancel_publish_access_record()
        """
        return self.model_api.cancel_publish_access_record(
            marketplace_demo=self, **kwargs
        )

    def provision(self, **kwargs: Any) -> Simulation:
        """Provision a simulation from this marketplace demo.

        Example:
            >>> simulation = marketplace_demo.provision()
            >>> print(simulation.name)
        """
        return self.model_api.provision(marketplace_demo=self, **kwargs)

    def manage(self, **kwargs: Any) -> MarketplaceDemo:
        """Adjust how this marketplace demo is featured and ordered.

        Privileged action (SRE/ADMIN). See
        :meth:`MarketplaceDemoEndpointAPI.manage`.

        Example:
            >>> marketplace_demo.manage(featured=True, order=1)
        """
        return self.model_api.manage(marketplace_demo=self, **kwargs)


class MarketplaceDemoEndpointAPI(
    MarketplaceDemoEndpointAPICompatMixin,
    BaseEndpointAPICompatMixin,
    mixins.ListApiMixin[MarketplaceDemo],
    mixins.CreateApiMixin[MarketplaceDemo],
    mixins.GetApiMixin[MarketplaceDemo],
    mixins.PatchApiMixin[MarketplaceDemo],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[MarketplaceDemo],
):
    """API client for marketplace demo endpoints."""

    API_PATH = 'marketplace/demos'
    API_PUBLISH_PATH = 'publish'
    API_UNPUBLISH_PATH = 'unpublish'
    API_PROVISION_PATH = 'provision'
    API_REQUEST_PUBLISH_PATH = 'request-publish'
    API_REQUEST_UNPUBLISH_PATH = 'request-unpublish'
    API_REQUEST_PUBLIC_PATH = 'request-public'
    API_REQUEST_ALLOWLIST_CHANGE_PATH = 'request-allowlist-change'
    API_CANCEL_PUBLISH_ACCESS_RECORD_PATH = 'cancel-publish-access-record'
    API_MANAGE_PATH = 'manage'
    API_TIGHTEN_ORDER_PATH = 'tighten-order'
    model = MarketplaceDemo

    @validate_payload_types
    def publish(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> None:
        """Publish a marketplace demo.

        A ``publisher`` must be set on the demo before it can be published.

        Example:
            >>> # Using demo object
            >>> api.marketplace_demos.publish(marketplace_demo=marketplace_demo)
            >>> # Or using ID
            >>> api.marketplace_demos.publish(marketplace_demo='marketplace-demo-id')
        """
        return self._patch_resource_action(
            marketplace_demo,
            self.API_PUBLISH_PATH,
            status_code=HTTPStatus.NO_CONTENT,
            **kwargs,
        )

    @validate_payload_types
    def unpublish(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> None:
        """Unpublish a marketplace demo.

        Example:
            >>> api.marketplace_demos.unpublish(marketplace_demo=marketplace_demo)
        """
        return self._patch_resource_action(
            marketplace_demo,
            self.API_UNPUBLISH_PATH,
            status_code=HTTPStatus.NO_CONTENT,
            **kwargs,
        )

    @validate_payload_types
    def provision(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> Simulation:
        """Provision a simulation from a marketplace demo.

        Creates a new simulation by cloning the demo simulation.

        Example:
            >>> # Using demo object
            >>> marketplace_demo = api.marketplace_demos.get('marketplace-demo-id')
            >>> simulation = marketplace_demo.provision()
            >>> print(simulation.id)
            >>> # Or using API directly with ID
            >>> demo_id = 'marketplace-demo-id'
            >>> simulation = api.marketplace_demos.provision(marketplace_demo=demo_id)
            >>> print(simulation.name)
        """
        marketplace_demo_id = (
            marketplace_demo.id
            if isinstance(marketplace_demo, MarketplaceDemo)
            else marketplace_demo
        )

        url = join_urls(self.url, str(marketplace_demo_id), self.API_PROVISION_PATH)
        response = self.__api__.client.post(url, data=mixins.serialize_payload(kwargs))

        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)

        if isinstance(marketplace_demo, MarketplaceDemo):
            marketplace_demo.refresh()

        # The API returns a Simulation object
        return self.__api__.simulations.load_model(response.json())

    @validate_payload_types
    def request_publish(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemo:
        """Submit a request to publish a marketplace demo.

        A ``publisher`` must be set on the demo — either previously or via this
        request (pass ``publisher=...``) — before it can be queued for publishing.

        Example:
            >>> api.marketplace_demos.request_publish(
            ...     marketplace_demo=marketplace_demo,
            ...     justification='Ready',
            ... )
        """
        return self._patch_resource_action(
            marketplace_demo, self.API_REQUEST_PUBLISH_PATH, **kwargs
        )

    @validate_payload_types
    def request_unpublish(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemo:
        """Submit a request to unpublish a marketplace demo.

        Example:
            >>> api.marketplace_demos.request_unpublish(
            ...     marketplace_demo=marketplace_demo,
            ...     justification='Deprecated',
            ... )
        """
        return self._patch_resource_action(
            marketplace_demo, self.API_REQUEST_UNPUBLISH_PATH, **kwargs
        )

    @validate_payload_types
    def request_public(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemo:
        """Submit a request to change marketplace demo visibility to public or restricted.

        Example:
            >>> api.marketplace_demos.request_public(
            ...     marketplace_demo=marketplace_demo,
            ...     prefer_public=True,
            ...     justification='Open source',
            ... )
        """
        return self._patch_resource_action(
            marketplace_demo, self.API_REQUEST_PUBLIC_PATH, **kwargs
        )

    @validate_payload_types
    def request_allowlist_change(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemo:
        """Submit a request to change the allowlist for a marketplace demo.

        Example:
            >>> api.marketplace_demos.request_allowlist_change(
            ...     marketplace_demo=marketplace_demo,
            ...     justification='Add partner orgs',
            ...     allowed_orgs_request_text='org-a, org-b',
            ... )
        """
        return self._patch_resource_action(
            marketplace_demo, self.API_REQUEST_ALLOWLIST_CHANGE_PATH, **kwargs
        )

    @validate_payload_types
    def cancel_publish_access_record(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemo:
        """Cancel the active publish access record for a marketplace demo.

        Example:
            >>> api.marketplace_demos.cancel_publish_access_record(
            ...     marketplace_demo=marketplace_demo,
            ... )
        """
        return self._patch_resource_action(
            marketplace_demo, self.API_CANCEL_PUBLISH_ACCESS_RECORD_PATH, **kwargs
        )

    @validate_payload_types
    def manage(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemo:
        """Adjust how a marketplace demo is featured and ordered.

        Privileged action (SRE/ADMIN). Featured demos appear before non-featured
        demos in the default ordering, and demos with a lower ``order`` value
        appear before demos with a higher ``order`` value.

        Example:
            >>> api.marketplace_demos.manage(
            ...     marketplace_demo=marketplace_demo,
            ...     featured=True,
            ...     order=1,
            ... )
        """
        return self._patch_resource_action(
            marketplace_demo, self.API_MANAGE_PATH, **kwargs
        )

    def tighten_order(self, **kwargs: Any) -> None:
        """Re-number marketplace demo ``order`` values to be consecutive from 1.

        Privileged action (SRE/ADMIN). Re-numbers the populated ``order`` values
        of marketplace demos so that they are consecutive starting at 1,
        preserving their relative ordering. For example, demos with
        ``order=[1, 5, 20]`` become ``[1, 2, 3]``. Demos with ``order=None`` are
        left untouched.

        Example:
            >>> api.marketplace_demos.tighten_order()
        """
        url = join_urls(self.url, self.API_TIGHTEN_ORDER_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(
            response, status_code=HTTPStatus.NO_CONTENT, data_type=None
        )
