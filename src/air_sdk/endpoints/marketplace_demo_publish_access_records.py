# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints import mixins
from air_sdk.endpoints.marketplace_demos import MarketplaceDemo
from air_sdk.utils import validate_payload_types


@dataclass(eq=False)
class MarketplaceDemoPublishAccessRecord(AirModel):
    """Represents a request to publish or change the visibility of a marketplace demo.

    Publish access records are created when an org requests to publish a marketplace demo
    or change its visibility. An admin must review the request and either
    approve or deny it.

    Attributes:
        id: Unique identifier for the record
        created: Timestamp when the record was created
        modified: Timestamp when the record was last modified
        marketplace_demo: The marketplace demo the request is for (foreign key —
            lazily resolved)
        marketplace_demo_name: Name of the marketplace demo at the time of the request
        requested_by: Email of the user who submitted the request, or None
        requested_at: Timestamp when the request was submitted, or None
        requesting_org: Org's readable_name (display_name or ngc_org_name), or None
        requesting_org_display_name: Display name of the requesting org, or None
        requesting_org_ngc_org_name: NGC org name of the requesting org, or None
        reviewed_by: Email of the admin who reviewed the request, or None
        reviewed_at: Timestamp when the request was reviewed, or None
        status: Current status of the request
        publicly_published: Whether the marketplace demo should be publicly accessible
        prefer_public: Whether the requester prefers public over allowlist
        justification: Requester's reason for the request
        allowed_orgs_request_text: Free-text description of orgs to allowlist
        allowed_orgs: List of org UUIDs on the allowlist, or None.
            Note: Only populated for admin callers; non-admins receive None.
        denial_reason: Reason the request was denied, or empty string if not yet denied
    """

    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    marketplace_demo: MarketplaceDemo = field(metadata=AirModel.FIELD_FOREIGN_KEY)
    marketplace_demo_name: str
    requested_by: str | None = field(repr=False)
    requested_at: datetime | None = field(repr=False)
    requesting_org: str | None = field(repr=False)
    requesting_org_display_name: str | None = field(repr=False)
    requesting_org_ngc_org_name: str | None = field(repr=False)
    reviewed_by: str | None = field(repr=False)
    reviewed_at: datetime | None = field(repr=False)
    status: str
    publicly_published: bool = field(repr=False)
    prefer_public: bool = field(repr=False)
    justification: str = field(repr=False)
    allowed_orgs_request_text: str = field(repr=False)
    allowed_orgs: list[str] | None = field(repr=False)
    denial_reason: str = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type['MarketplaceDemoPublishAccessRecordEndpointAPI']:
        """Returns the respective `AirModelAPI` type for this model"""
        return MarketplaceDemoPublishAccessRecordEndpointAPI

    @property
    def model_api(self) -> 'MarketplaceDemoPublishAccessRecordEndpointAPI':
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    def approve(self, **kwargs: Any) -> 'MarketplaceDemoPublishAccessRecord':
        """Approve this request.

        See ``MarketplaceDemoPublishAccessRecordEndpointAPI.approve``.
        """
        return self.model_api.approve(record=self, **kwargs)

    def deny(self, **kwargs: Any) -> 'MarketplaceDemoPublishAccessRecord':
        """Deny this request.

        See ``MarketplaceDemoPublishAccessRecordEndpointAPI.deny``.
        """
        return self.model_api.deny(record=self, **kwargs)

    def set_visibility(self, **kwargs: Any) -> 'MarketplaceDemoPublishAccessRecord':
        """Set visibility.

        See ``MarketplaceDemoPublishAccessRecordEndpointAPI.set_visibility``.
        """
        return self.model_api.set_visibility(record=self, **kwargs)


class MarketplaceDemoPublishAccessRecordEndpointAPI(
    mixins.ListApiMixin[MarketplaceDemoPublishAccessRecord],
    mixins.GetApiMixin[MarketplaceDemoPublishAccessRecord],
    BaseEndpointAPI[MarketplaceDemoPublishAccessRecord],
):
    """Endpoint API for managing marketplace demo publish access records.

    Provides methods for listing and retrieving records, plus admin actions
    to approve, deny, or change the visibility of a pending request.
    Records are created automatically by the Air platform when a publish
    or visibility-change request is submitted — they cannot be created via
    the SDK.
    """

    API_PATH = 'publishing/marketplace-demo-publish-access-records'
    API_APPROVE_PATH = 'approve'
    API_DENY_PATH = 'deny'
    API_SET_VISIBILITY_PATH = 'set-visibility'
    model = MarketplaceDemoPublishAccessRecord

    @validate_payload_types
    def approve(
        self, *, record: MarketplaceDemoPublishAccessRecord | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemoPublishAccessRecord:
        """Approve a pending publish access request.

        Example:
            >>> record = api.marketplace_demo_publish_access_records.get('record-uuid')
            >>> api.marketplace_demo_publish_access_records.approve(record=record)

            >>> # Approve with explicit visibility
            >>> api.marketplace_demo_publish_access_records.approve(
            ...     record=record,
            ...     publicly_published=True,
            ... )
        """
        return self._patch_resource_action(record, self.API_APPROVE_PATH, **kwargs)

    @validate_payload_types
    def deny(
        self, *, record: MarketplaceDemoPublishAccessRecord | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemoPublishAccessRecord:
        """Deny a pending publish access request.

        Example:
            >>> api.marketplace_demo_publish_access_records.deny(
            ...     record='record-uuid',
            ...     denial_reason='Does not meet publishing requirements.',
            ... )
        """
        return self._patch_resource_action(record, self.API_DENY_PATH, **kwargs)

    @validate_payload_types
    def set_visibility(
        self, *, record: MarketplaceDemoPublishAccessRecord | PrimaryKey, **kwargs: Any
    ) -> MarketplaceDemoPublishAccessRecord:
        """Update the visibility of a published marketplace demo.

        Example:
            >>> # Make marketplace demo public
            >>> api.marketplace_demo_publish_access_records.set_visibility(
            ...     record='record-uuid',
            ...     publicly_published=True,
            ... )

            >>> # Restrict to specific orgs
            >>> api.marketplace_demo_publish_access_records.set_visibility(
            ...     record='record-uuid',
            ...     publicly_published=False,
            ...     allowed_orgs=['org-uuid-1', 'org-uuid-2'],
            ... )
        """
        return self._patch_resource_action(record, self.API_SET_VISIBILITY_PATH, **kwargs)
