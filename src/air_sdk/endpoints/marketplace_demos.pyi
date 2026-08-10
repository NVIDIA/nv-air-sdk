# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for marketplace demos endpoint type hints.
"""

from dataclasses import _MISSING_TYPE, dataclass
from datetime import datetime
from typing import Any, Iterator, List

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.simulations import Simulation
from air_sdk.types import DEMO_SIMULATION_STATE, SimRequiredResources

@dataclass(eq=False)
class MarketplaceDemo(AirModel):
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
        publisher: The name of the company or organization the marketplace demo is
            published under (e.g. NVIDIA, Google). A publisher must be set before the
            demo can be published.
        tags: The tags of the marketplace demo
        published: Whether the marketplace demo is published
        expected_resource_usage: Estimated resources required to provision the demo
        icon: The icon of the marketplace demo
        demo: Demo simulation to be used as a base for cloned simulations.
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
    demo: Simulation
    created: datetime
    modified: datetime
    creator: str
    documentation: str | None
    tags: list[str]
    published: bool
    publicly_published: bool
    demo_simulation_state: DEMO_SIMULATION_STATE
    expected_resource_usage: SimRequiredResources
    description: str | None
    repo: str | None
    publisher: str
    icon: str | None
    publish_access_record_id: str | None
    featured: bool
    order: int | None
    provision_count: int

    @classmethod
    def get_model_api(cls) -> type[MarketplaceDemoEndpointAPI]: ...
    @property
    def model_api(self) -> MarketplaceDemoEndpointAPI: ...
    def update(  # type: ignore[override]
        self,
        *,
        name: str | _MISSING_TYPE = ...,
        description: str | None | _MISSING_TYPE = ...,
        documentation: str | None | _MISSING_TYPE = ...,
        repo: str | None | _MISSING_TYPE = ...,
        publisher: str | _MISSING_TYPE = ...,
        tags: list[str] | _MISSING_TYPE = ...,
        icon: str | None | _MISSING_TYPE = ...,
    ) -> MarketplaceDemo:
        """
        Update the marketplace demo's properties.

        Args:
            name: New name for the marketplace demo
            description: Description of the marketplace demo
            documentation: Documentation of the marketplace demo
            repo: Repository of the marketplace demo
            publisher: The company or organization the demo is published under
                (e.g. NVIDIA, Google). Required before the demo can be published.
            tags: Tags of the marketplace demo
            icon: Icon of the marketplace demo

        Returns:
            The updated MarketplaceDemo instance

        Example:
            >>> marketplace_demo.update(name='New Name', description='New Desc')
            >>> print(marketplace_demo.name)
        """
        ...

    def publish(
        self,
        *,
        prefer_public: bool = ...,
        allowed_orgs: list[PrimaryKey] = ...,
        justification: str = ...,
        publish_images: bool = ...,
        **kwargs: Any,
    ) -> None:
        """
        Publish the marketplace demo.

        A ``publisher`` must be set on the demo before it can be published.

        Args:
            prefer_public: Whether to publish as public (``true``, default) or
                restricted (``false``). When ``false``, supply the authoritative
                ``allowed_orgs``.
            allowed_orgs: Authoritative allow-list: orgs that may use the demo when
                ``prefer_public`` is ``false``. The demo owning org is always
                included; ``[]`` is valid. Privileged endpoint only — not the gated
                ``request-publish`` string hint.
            justification: Optional text explaining who/why to share with.
            publish_images: When ``true``, automatically publish org-owned images
                referenced by the demo so they reach the same audience as the demo.
                When ``false`` (default), the request is rejected with 400 if any
                referenced image needs to be published to reach the demo audience.

        Example:
            >>> marketplace_demo.publish()
        """
        ...

    def unpublish(self, **kwargs: Any) -> None:
        """
        Immediately unpublish the marketplace demo (privileged).

        This privileged action takes no request body. To submit a gated unpublish
        request for review instead, use :meth:`request_unpublish`.

        Example:
            >>> marketplace_demo.unpublish()
        """
        ...

    def provision(self, **kwargs: Any) -> Simulation:
        """
        Provision a simulation from this marketplace demo.

        Returns:
            Simulation: The newly created simulation instance.

        Example:
            >>> simulation = marketplace_demo.provision()
            >>> print(simulation.name)
        """
        ...

    def request_publish(
        self,
        *,
        justification: str,
        prefer_public: bool = ...,
        allowed_orgs_request_text: str = ...,
        publish_images: bool = ...,
        publisher: str = ...,
        tags: list[str] = ...,
    ) -> MarketplaceDemo:
        """Submit a request to publish this marketplace demo.

        A ``publisher`` must be set on the demo — either previously or via this
        request — before the demo can be queued for publishing.

        Args:
            justification: Required explanation for the review request and
                notifications.
            prefer_public: When true, the requester prefers a public publish. When
                false, the requester prefers a restricted-access publish; describe the
                desired allow list in ``allowed_orgs_request_text``.
            allowed_orgs_request_text: Optional free-text description of orgs that
                should have access if the outcome is restricted. Not the authoritative
                allow list.
            publish_images: When ``true``, automatically publish org-owned images
                referenced by the demo so they reach the same audience as the demo.
                When ``false`` (default), the request is rejected with 400 if any
                referenced image needs to be published to reach the demo audience.
            publisher: Optional publisher name to set on the demo when submitting
                the request (e.g. NVIDIA, Google). Omitting the field leaves the
                existing ``publisher`` unchanged.
            tags: Optional tag names to assign to the demo when submitting the
                request (same rules as demo update). Omitting the field leaves the
                demo's existing tags unchanged; an empty list clears them.

        Returns:
            MarketplaceDemo: the marketplace demo instance with updated
            publish_access_record_id

        Example:
            >>> marketplace_demo.request_publish(justification='Ready for community use')
        """
        ...

    def request_unpublish(
        self,
        *,
        justification: str,
    ) -> MarketplaceDemo:
        """Submit a request to unpublish this marketplace demo.

        Args:
            justification: Required explanation for the review request and
                notifications.

        Returns:
            MarketplaceDemo: the marketplace demo instance

        Example:
            >>> marketplace_demo.request_unpublish(justification='No longer maintained')
        """
        ...

    def request_public(
        self,
        *,
        prefer_public: bool,
        justification: str,
        publish_images: bool = ...,
    ) -> MarketplaceDemo:
        """Submit a request to change marketplace demo visibility to public or restricted.

        Args:
            prefer_public: When true, request catalog-wide visibility. When false,
                request restricted visibility.
            justification: Required explanation for the review request and
                notifications.
            publish_images: When ``true``, automatically publish org-owned images
                referenced by the demo so they reach the same audience as the demo.
                When ``false`` (default), the request is rejected with 400 if any
                referenced image needs to be published to reach the demo audience.

        Returns:
            MarketplaceDemo: the marketplace demo instance

        Example:
            >>> marketplace_demo.request_public(
            ...     prefer_public=True,
            ...     justification='Open source',
            ...     publish_images=True,
            ... )
        """
        ...

    def request_allowlist_change(
        self,
        *,
        justification: str,
        allowed_orgs_request_text: str,
        publish_images: bool = ...,
    ) -> MarketplaceDemo:
        """Submit a request to change the allowlist for this marketplace demo.

        Args:
            justification: Required explanation for the review request and
                notifications.
            allowed_orgs_request_text: Required description of the allow-list change
                (e.g. org names or IDs).
            publish_images: When ``true``, automatically publish org-owned images
                referenced by the demo so they reach the same audience as the demo.
                When ``false`` (default), the request is rejected with 400 if any
                referenced image needs to be published to reach the demo audience.

        Returns:
            MarketplaceDemo: the marketplace demo instance

        Example:
            >>> marketplace_demo.request_allowlist_change(
            ...     justification='Add partner orgs',
            ...     allowed_orgs_request_text='org-a, org-b',
            ... )
        """
        ...

    def cancel_publish_access_record(self, **kwargs: Any) -> MarketplaceDemo:
        """Cancel the active publish access record for this marketplace demo.

        Returns:
            MarketplaceDemo: the marketplace demo instance

        Example:
            >>> marketplace_demo.cancel_publish_access_record()
        """
        ...

    def manage(
        self,
        *,
        featured: bool = ...,
        order: int | None = ...,
        **kwargs: Any,
    ) -> MarketplaceDemo:
        """Adjust how this marketplace demo is featured and ordered.

        Privileged action (SRE/ADMIN). See
        :meth:`MarketplaceDemoEndpointAPI.manage`.

        Args:
            featured: Whether the demo is featured. Featured demos appear before
                non-featured demos in the default ordering.
            order: The ordering value of the demo. Demos with a lower ``order``
                value appear before demos with a higher ``order`` value. Pass
                ``None`` to clear the demo's order.

        Returns:
            MarketplaceDemo: the updated marketplace demo instance

        Example:
            >>> marketplace_demo.manage(featured=True, order=1)
        """
        ...

class MarketplaceDemoEndpointAPI(BaseEndpointAPI[MarketplaceDemo]):
    """
    API client for marketplace demo endpoints."""

    API_PATH: str
    API_PUBLISH_PATH: str
    API_UNPUBLISH_PATH: str
    API_PROVISION_PATH: str
    API_REQUEST_PUBLISH_PATH: str
    API_REQUEST_UNPUBLISH_PATH: str
    API_REQUEST_PUBLIC_PATH: str
    API_REQUEST_ALLOWLIST_CHANGE_PATH: str
    API_CANCEL_PUBLISH_ACCESS_RECORD_PATH: str
    API_MANAGE_PATH: str
    API_TIGHTEN_ORDER_PATH: str
    model: type[MarketplaceDemo]

    def create(
        self,
        *,
        name: str,
        simulation: str,
        description: str | None | _MISSING_TYPE = ...,
        documentation: str | None | _MISSING_TYPE = ...,
        repo: str | None | _MISSING_TYPE = ...,
        publisher: str | _MISSING_TYPE = ...,
        tags: list[str] | _MISSING_TYPE = ...,
        icon: str | None | _MISSING_TYPE = ...,
        checkpoint: str | None | _MISSING_TYPE = ...,
    ) -> MarketplaceDemo:
        """
        Create a new marketplace demo.

        Args:
            name: Name for the new marketplace demo
            simulation: Simulation to be used to provision the marketplace demo
            description: Description of the marketplace demo
            documentation: Documentation of the marketplace demo
            repo: Repository of the marketplace demo
            publisher: The company or organization the demo is published under
                (e.g. NVIDIA, Google). Required before the demo can be published.
            tags: Tags of the marketplace demo
            icon: Icon of the marketplace demo
            checkpoint: A COMPLETE checkpoint to clone from.
                       Provided checkpoint must belong to the simulation.
                       If not specified, latest COMPLETE checkpoint will be used.

        Returns:
            The created MarketplaceDemo instance

        Example:
            >>> marketplace_demo = api.marketplace_demos.create(
            ...     name='My Marketplace Demo',
            ...     simulation='sim-id',
            ...     description='My Demo Description',
            ...     documentation='My Demo Documentation',
            ...     repo='My Demo Repo',
            ...     tags=['networking', 'sonic'],
            ... )

        """
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """
        Delete a marketplace demo.

        Args:
            pk: The marketplace demo ID (string or UUID)

        Example:
            >>> api.marketplace_demos.delete('marketplace-demo-id')
        """
        ...

    def list(  # type: ignore[override]
        self,
        *,
        demo_simulation_state: DEMO_SIMULATION_STATE | _MISSING_TYPE = ...,
        creator: str | _MISSING_TYPE = ...,
        tags: list[str] | _MISSING_TYPE = ...,
        published: bool | _MISSING_TYPE = ...,
        publicly_published: bool | _MISSING_TYPE = ...,
        featured: bool | _MISSING_TYPE = ...,
        publisher: str | _MISSING_TYPE = ...,
        search: str | _MISSING_TYPE = ...,
        ordering: str | _MISSING_TYPE = ...,
        limit: int | _MISSING_TYPE = ...,
        offset: int | _MISSING_TYPE = ...,
    ) -> Iterator[MarketplaceDemo]:
        """
        List all marketplace demos.

        Optional parameters:
            demo_simulation_state: Filter by the state of the template simulation
            creator: Filter by creator email
            tags: Filter by tags (matched case-insensitively)
            published: Filter by published status (true or false)
            publicly_published: Filter by publicly published status (true or false)
            featured: Filter by whether the demo is featured (true or false). Featured
                demos are listed before non-featured demos in the default ordering.
            publisher: Filter by the company or organization the demo is published
                under (e.g. NVIDIA). Matched case-insensitively.
            search: Search term to filter demos
            ordering: Order the response by the specified field
            limit: Number of results to return per page
            offset: The initial index from which to return the results

        Returns:
            Iterator of MarketplaceDemo instances

        Example:
            >>> # List all demos
            >>> for demo in api.marketplace_demos.list():
            ...     print(demo.name)
            >>> # List with filters
            >>> results = list(
            ...     api.marketplace_demos.list(
            ...         creator='test@example.com',
            ...         published=True,
            ...         tags=['networking'],
            ...     )
            ... )

        """
        ...

    def get(self, pk: PrimaryKey) -> MarketplaceDemo:
        """
        Get a specific marketplace demo by ID.

        Args:
            pk: The marketplace demo ID (string or UUID)

        Returns:
            The MarketplaceDemo instance

        Example:
            >>> marketplace_demo = api.marketplace_demos.get('marketplace-demo-id')
            >>> print(marketplace_demo.name)

        """
        ...

    def publish(
        self,
        *,
        marketplace_demo: MarketplaceDemo | PrimaryKey,
        prefer_public: bool = ...,
        allowed_orgs: List[PrimaryKey] = ...,
        justification: str = ...,
        publish_images: bool = ...,
        **kwargs: Any,
    ) -> None:
        """
        Publish a marketplace demo.

        A ``publisher`` must be set on the demo before it can be published.

        Args:
            marketplace_demo: The marketplace demo to publish (object or ID)
            prefer_public: Whether to publish as public (``true``, default) or
                restricted (``false``). When ``false``, supply the authoritative
                ``allowed_orgs``.
            allowed_orgs: Authoritative allow-list: orgs that may use the demo when
                ``prefer_public`` is ``false``. The demo owning org is always
                included; ``[]`` is valid. Privileged endpoint only — not the gated
                ``request-publish`` string hint.
            justification: Optional text explaining who/why to share with.
            publish_images: When ``true``, automatically publish org-owned images
                referenced by the demo so they reach the same audience as the demo.
                When ``false`` (default), the request is rejected with 400 if any
                referenced image needs to be published to reach the demo audience.

        Returns:
            None

        Example:
            >>> # Using demo object
            >>> api.marketplace_demos.publish(marketplace_demo=marketplace_demo)
            >>> # Or using ID
            >>> api.marketplace_demos.publish(marketplace_demo='marketplace-demo-id')

        """
        ...

    def unpublish(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> None:
        """
        Unpublish a marketplace demo.

        Args:
            marketplace_demo: The marketplace demo to unpublish (object or ID)

        Returns:
            None

        Example:
            >>> api.marketplace_demos.unpublish(marketplace_demo=marketplace_demo)

        """
        ...

    def provision(
        self, *, marketplace_demo: MarketplaceDemo | PrimaryKey, **kwargs: Any
    ) -> Simulation:
        """
        Provision a simulation from a marketplace demo.

        Creates a new simulation by cloning the demo simulation.

        Args:
            marketplace_demo: The marketplace demo to provision (object or ID)

        Returns:
            Simulation: The newly created simulation instance.

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
        ...
    def request_publish(
        self,
        *,
        marketplace_demo: MarketplaceDemo | PrimaryKey,
        justification: str,
        prefer_public: bool = ...,
        allowed_orgs_request_text: str = ...,
        publish_images: bool = ...,
        publisher: str = ...,
        tags: List[str] = ...,
    ) -> MarketplaceDemo:
        """Submit a request to publish a marketplace demo.

        A ``publisher`` must be set on the demo — either previously or via this
        request — before the demo can be queued for publishing.

        Args:
        Required parameters:
            marketplace_demo: Marketplace demo to request publication for
                (MarketplaceDemo instance or marketplace demo ID)
            justification: Required explanation for the review request and
                notifications.

        Optional parameters:
            prefer_public: When true, the requester prefers a public publish. When
                false, the requester prefers a restricted-access publish; describe the
                desired allow list in ``allowed_orgs_request_text``.
            allowed_orgs_request_text: Optional free-text description of orgs that
                should have access if the outcome is restricted. Not the authoritative
                allow list.
            publish_images: When ``true``, automatically publish org-owned images
                referenced by the demo so they reach the same audience as the demo.
                When ``false`` (default), the request is rejected with 400 if any
                referenced image needs to be published to reach the demo audience.
            publisher: Optional publisher name to set on the demo when submitting
                the request (e.g. NVIDIA, Google). Omitting the field leaves the
                existing ``publisher`` unchanged.
            tags: Optional tag names to assign to the demo when submitting the
                request (same rules as demo update). Omitting the field leaves the
                demo's existing tags unchanged; an empty list clears them.

        Returns:
            MarketplaceDemo: the marketplace demo instance with updated
            publish_access_record_id

        Example:
            >>> api.marketplace_demos.request_publish(
            ...     marketplace_demo=marketplace_demo,
            ...     justification='Ready',
            ... )
        """
        ...

    def request_unpublish(
        self,
        *,
        marketplace_demo: MarketplaceDemo | PrimaryKey,
        justification: str,
    ) -> MarketplaceDemo:
        """Submit a request to unpublish a marketplace demo.

        Args:
        Required parameters:
            marketplace_demo: Marketplace demo to request unpublication for
                (MarketplaceDemo instance or marketplace demo ID)
            justification: Required explanation for the review request and
                notifications.

        Returns:
            MarketplaceDemo: the marketplace demo instance

        Example:
            >>> api.marketplace_demos.request_unpublish(
            ...     marketplace_demo=marketplace_demo,
            ...     justification='Deprecated',
            ... )
        """
        ...

    def request_public(
        self,
        *,
        marketplace_demo: MarketplaceDemo | PrimaryKey,
        prefer_public: bool,
        justification: str,
        publish_images: bool = ...,
    ) -> MarketplaceDemo:
        """Submit a request to change marketplace demo visibility to public or restricted.

        Args:
        Required parameters:
            marketplace_demo: Marketplace demo to update (MarketplaceDemo instance or
                marketplace demo ID)
            prefer_public: When true, request catalog-wide visibility. When false,
                request restricted visibility.
            justification: Required explanation for the review request and
                notifications.

        Optional parameters:
            publish_images: When ``true``, automatically publish org-owned images
                referenced by the demo so they reach the same audience as the demo.
                When ``false`` (default), the request is rejected with 400 if any
                referenced image needs to be published to reach the demo audience.

        Returns:
            MarketplaceDemo: the marketplace demo instance

        Example:
            >>> api.marketplace_demos.request_public(
            ...     marketplace_demo=marketplace_demo,
            ...     prefer_public=True,
            ...     justification='Open source',
            ... )
        """
        ...

    def request_allowlist_change(
        self,
        *,
        marketplace_demo: MarketplaceDemo | PrimaryKey,
        justification: str,
        allowed_orgs_request_text: str,
        publish_images: bool = ...,
    ) -> MarketplaceDemo:
        """Submit a request to change the allowlist for a marketplace demo.

        Args:
        Required parameters:
            marketplace_demo: Marketplace demo to update (MarketplaceDemo instance or
                marketplace demo ID)
            justification: Required explanation for the review request and
                notifications.
            allowed_orgs_request_text: Required description of the allow-list change
                (e.g. org names or IDs).

        Optional parameters:
            publish_images: When ``true``, automatically publish org-owned images
                referenced by the demo so they reach the same audience as the demo.
                When ``false`` (default), the request is rejected with 400 if any
                referenced image needs to be published to reach the demo audience.

        Returns:
            MarketplaceDemo: the marketplace demo instance

        Example:
            >>> api.marketplace_demos.request_allowlist_change(
            ...     marketplace_demo=marketplace_demo,
            ...     justification='Add partner orgs',
            ...     allowed_orgs_request_text='org-a, org-b',
            ... )
        """
        ...

    def cancel_publish_access_record(
        self,
        *,
        marketplace_demo: MarketplaceDemo | PrimaryKey,
    ) -> MarketplaceDemo:
        """Cancel the active publish access record for a marketplace demo.

        Args:
        Required parameters:
            marketplace_demo: Marketplace demo to cancel the record for (MarketplaceDemo
                instance or marketplace demo ID)

        Returns:
            MarketplaceDemo: the marketplace demo instance

        Example:
            >>> api.marketplace_demos.cancel_publish_access_record(
            ...     marketplace_demo=marketplace_demo,
            ... )
        """
        ...

    def manage(
        self,
        *,
        marketplace_demo: MarketplaceDemo | PrimaryKey,
        featured: bool = ...,
        order: int | None = ...,
        **kwargs: Any,
    ) -> MarketplaceDemo:
        """Adjust how a marketplace demo is featured and ordered.

        Privileged action (SRE/ADMIN). Featured demos appear before non-featured
        demos in the default ordering, and demos with a lower ``order`` value
        appear before demos with a higher ``order`` value.

        Args:
        Required parameters:
            marketplace_demo: Marketplace demo to manage (MarketplaceDemo instance
                or marketplace demo ID)

        Optional parameters:
            featured: Whether the demo is featured.
            order: The ordering value of the demo. Pass ``None`` to clear the
                demo's order.

        Returns:
            MarketplaceDemo: the updated marketplace demo instance

        Example:
            >>> api.marketplace_demos.manage(
            ...     marketplace_demo=marketplace_demo,
            ...     featured=True,
            ...     order=1,
            ... )
        """
        ...

    def tighten_order(self, **kwargs: Any) -> None:
        """Re-number marketplace demo ``order`` values to be consecutive from 1.

        Privileged action (SRE/ADMIN). Re-numbers the populated ``order`` values
        of marketplace demos so that they are consecutive starting at 1,
        preserving their relative ordering. For example, demos with
        ``order=[1, 5, 20]`` become ``[1, 2, 3]``. Demos with ``order=None`` are
        left untouched.

        Returns:
            None

        Example:
            >>> api.marketplace_demos.tighten_order()
        """
        ...
