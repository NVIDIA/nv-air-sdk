# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.marketplace_demo_publish_access_records import (
    MarketplaceDemoPublishAccessRecord,
)
from air_sdk.types import ACCESS_REQUEST_STATUS

@dataclass(eq=False)
class MarketplaceDemoAccessRequest(AirModel):
    """An organization's request for access to a preview marketplace demo.

    A marketplace demo published restrictively may also be marked as *preview*, which
    lets every authenticated user see the demo and its documentation while keeping
    provisioning restricted to the allowlisted orgs. Orgs that cannot yet provision
    such a demo submit an access request via
    ``MarketplaceDemo.request_access()``. An admin then accepts the request — which
    adds the requesting org to the demo's allowlist — or denies it.

    There is one access request per org per demo; re-requesting updates the existing
    record rather than creating another.

    Note:
        Only admins can ``refresh()`` an access request, and only admins and the demo's
        owning org can resolve ``publish_access_record``. Requesters should re-read
        their request with ``MarketplaceDemo.get_access_request()`` instead.

    Attributes:
        id: Unique identifier for the access request
        created: Timestamp when the access request was created
        modified: Timestamp when the access request was last modified
        publish_access_record: The publish access record governing the demo this
            request is for (foreign key — lazily resolved; admins and the demo's owning
            org only)
        marketplace_demo: UUID of the marketplace demo access was requested for
        marketplace_demo_name: Name of the marketplace demo, or None
        requesting_org: Requesting org's readable_name (display_name or
            ngc_org_name), or None
        requesting_org_display_name: Display name of the requesting org, or None
        requesting_org_ngc_org_name: NGC org name of the requesting org, or None
        requested_by: Emails of the users from the requesting org who submitted or
            re-submitted this request
        requested_at: Timestamp when the request was most recently submitted, or None
        reviewed_by: Email of the admin who last reviewed the request, or None
        reviewed_at: Timestamp when the request was last reviewed, or None
        status: Current status of the access request
        company_name: Free-text company name supplied by the requester. Not derived
            from the requesting org.
        justification: Requester's explanation of why access is needed. Same-org
            re-submissions append further entries rather than replacing this.
        denial_reason: Reason the request was denied, or empty string if not denied
    """

    id: str
    created: datetime
    modified: datetime
    publish_access_record: MarketplaceDemoPublishAccessRecord
    marketplace_demo: str
    marketplace_demo_name: str | None
    requesting_org: str | None
    requesting_org_display_name: str | None
    requesting_org_ngc_org_name: str | None
    requested_by: list[str]
    requested_at: datetime | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    status: ACCESS_REQUEST_STATUS
    company_name: str
    justification: str
    denial_reason: str

    @classmethod
    def get_model_api(cls) -> type[MarketplaceDemoAccessRequestEndpointAPI]: ...
    @property
    def model_api(self) -> MarketplaceDemoAccessRequestEndpointAPI: ...
    def accept(self, **kwargs: Any) -> MarketplaceDemoAccessRequest:
        """Accept this access request.

        See ``MarketplaceDemoAccessRequestEndpointAPI.accept``.
        """
        ...

    def deny(
        self,
        *,
        denial_reason: str = ...,
        **kwargs: Any,
    ) -> MarketplaceDemoAccessRequest:
        """Deny this access request.

        See ``MarketplaceDemoAccessRequestEndpointAPI.deny``.
        """
        ...

class MarketplaceDemoAccessRequestEndpointAPI(
    BaseEndpointAPI[MarketplaceDemoAccessRequest]
):
    """Endpoint API for reviewing marketplace demo access requests.

    Provides methods for listing and retrieving access requests, plus admin actions
    to accept or deny an open request. Listing and retrieving require admin
    privileges; use ``MarketplaceDemo.get_access_request()`` to read your own
    organization's request for a demo.

    Access requests are created by requesting access to a preview demo — see
    ``MarketplaceDemo.request_access()`` — and cannot be created directly via this
    endpoint.
    """

    API_PATH: str
    API_ACCEPT_PATH: str
    API_DENY_PATH: str
    model: type[MarketplaceDemoAccessRequest]

    def list(  # type: ignore[override]
        self,
        *,
        marketplace_demo: str | PrimaryKey = ...,
        publish_access_record: str | PrimaryKey = ...,
        requesting_org: str | PrimaryKey = ...,
        status: ACCESS_REQUEST_STATUS = ...,
        requesting_org_display_name: str = ...,
        requesting_org_ngc_org_name: str = ...,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
    ) -> Iterator[MarketplaceDemoAccessRequest]:
        """List marketplace demo access requests.

        Requires admin privileges. To read your own organization's request for a
        single demo, use ``MarketplaceDemo.get_access_request()`` instead.

        Args:
            marketplace_demo: Filter by marketplace demo UUID
            publish_access_record: Filter by publish access record UUID
            requesting_org: Filter by requesting org UUID
            status: Filter by access request status
            requesting_org_display_name: Filter by org display name (case-insensitive)
            requesting_org_ngc_org_name: Filter by org NGC name (case-insensitive)
            limit: Number of results to return per page
            offset: Initial index from which to return results
            ordering: Order by field (prefix with ``-`` for descending). Supported
                fields: ``company_name``, ``created``, ``modified``, ``status``,
                ``requested_at``, ``reviewed_at``, ``marketplace_demo_name``,
                ``requesting_org_display_name``, ``requesting_org_ngc_org_name``.
            search: Search query matched against ``company_name``,
                ``justification``, ``marketplace_demo_name``, and the requesting
                org's display and NGC names

        Returns:
            Iterator of MarketplaceDemoAccessRequest instances

        Example:
            >>> requests = api.marketplace_demo_access_requests
            >>> for request in requests.list(status='REQUESTED'):
            ...     print(request.marketplace_demo_name, request.requesting_org)
        """
        ...

    def get(self, pk: PrimaryKey, **kwargs: Any) -> MarketplaceDemoAccessRequest:
        """Retrieve a specific access request.

        Requires admin privileges.

        Args:
            pk: Access request UUID
            **kwargs: Additional query parameters

        Returns:
            MarketplaceDemoAccessRequest instance

        Example:
            >>> request = api.marketplace_demo_access_requests.get('request-uuid')
            >>> print(request.status, request.company_name)
        """
        ...

    def accept(
        self,
        *,
        access_request: MarketplaceDemoAccessRequest | PrimaryKey,
        **kwargs: Any,
    ) -> MarketplaceDemoAccessRequest:
        """Accept an open access request.

        Adds the requesting organization to the demo's allowlist so it can
        provision the preview demo.

        Args:
            access_request: The access request to accept (instance or UUID)
            **kwargs: Additional parameters

        Returns:
            Updated MarketplaceDemoAccessRequest with status ``GRANTED``

        Example:
            >>> request = api.marketplace_demo_access_requests.get('request-uuid')
            >>> api.marketplace_demo_access_requests.accept(access_request=request)
        """
        ...

    def deny(
        self,
        *,
        access_request: MarketplaceDemoAccessRequest | PrimaryKey,
        denial_reason: str = ...,
        **kwargs: Any,
    ) -> MarketplaceDemoAccessRequest:
        """Deny an open access request.

        Args:
            access_request: The access request to deny (instance or UUID)
            denial_reason: Human-readable explanation of why access was denied
            **kwargs: Additional parameters

        Returns:
            Updated MarketplaceDemoAccessRequest with status ``DENIED``

        Example:
            >>> api.marketplace_demo_access_requests.deny(
            ...     access_request='request-uuid',
            ...     denial_reason='Not eligible for this demo.',
            ... )
        """
        ...
