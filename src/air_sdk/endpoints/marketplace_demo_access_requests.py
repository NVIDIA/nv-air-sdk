# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints import mixins
from air_sdk.endpoints.marketplace_demo_publish_access_records import (
    MarketplaceDemoPublishAccessRecord,
)
from air_sdk.utils import validate_payload_types


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

    Attributes:
        id: Unique identifier for the access request
        created: Timestamp when the access request was created
        modified: Timestamp when the access request was last modified
        publish_access_record: The publish access record governing the demo this
            request is for (foreign key — lazily resolved)
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

    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    publish_access_record: MarketplaceDemoPublishAccessRecord = field(
        metadata=AirModel.FIELD_FOREIGN_KEY, repr=False
    )
    marketplace_demo: str = field(repr=False)
    marketplace_demo_name: str | None
    requesting_org: str | None = field(repr=False)
    requesting_org_display_name: str | None = field(repr=False)
    requesting_org_ngc_org_name: str | None = field(repr=False)
    requested_by: list[str] = field(repr=False)
    requested_at: datetime | None = field(repr=False)
    reviewed_by: str | None = field(repr=False)
    reviewed_at: datetime | None = field(repr=False)
    status: str
    company_name: str = field(repr=False)
    justification: str = field(repr=False)
    denial_reason: str = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type['MarketplaceDemoAccessRequestEndpointAPI']:
        """Returns the respective `AirModelAPI` type for this model"""
        return MarketplaceDemoAccessRequestEndpointAPI

    @property
    def model_api(self) -> 'MarketplaceDemoAccessRequestEndpointAPI':
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    def accept(self, **kwargs: Any) -> 'MarketplaceDemoAccessRequest':
        """Accept this access request.

        See ``MarketplaceDemoAccessRequestEndpointAPI.accept``.
        """
        return self.model_api.accept(access_request=self, **kwargs)

    def deny(self, **kwargs: Any) -> 'MarketplaceDemoAccessRequest':
        """Deny this access request.

        See ``MarketplaceDemoAccessRequestEndpointAPI.deny``.
        """
        return self.model_api.deny(access_request=self, **kwargs)


class MarketplaceDemoAccessRequestEndpointAPI(
    mixins.ListApiMixin[MarketplaceDemoAccessRequest],
    mixins.GetApiMixin[MarketplaceDemoAccessRequest],
    BaseEndpointAPI[MarketplaceDemoAccessRequest],
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

    API_PATH = 'publishing/marketplace-demo-access-requests'
    API_ACCEPT_PATH = 'accept'
    API_DENY_PATH = 'deny'
    model = MarketplaceDemoAccessRequest

    @validate_payload_types
    def accept(
        self, *, access_request: MarketplaceDemoAccessRequest | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemoAccessRequest:
        """Accept an open access request.

        Adds the requesting organization to the demo's allowlist so it can
        provision the preview demo.

        Example:
            >>> request = api.marketplace_demo_access_requests.get('request-uuid')
            >>> api.marketplace_demo_access_requests.accept(access_request=request)
        """
        return self._patch_resource_action(access_request, self.API_ACCEPT_PATH, **kwargs)

    @validate_payload_types
    def deny(
        self, *, access_request: MarketplaceDemoAccessRequest | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemoAccessRequest:
        """Deny an open access request.

        Example:
            >>> api.marketplace_demo_access_requests.deny(
            ...     access_request='request-uuid',
            ...     denial_reason='Not eligible for this demo.',
            ... )
        """
        return self._patch_resource_action(access_request, self.API_DENY_PATH, **kwargs)
