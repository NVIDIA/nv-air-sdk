# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, List

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.marketplace_demos import MarketplaceDemo
from air_sdk.types import PAR_STATUS

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

    id: str
    created: datetime
    modified: datetime
    marketplace_demo: MarketplaceDemo
    marketplace_demo_name: str
    requested_by: str | None
    requested_at: datetime | None
    requesting_org: str | None
    requesting_org_display_name: str | None
    requesting_org_ngc_org_name: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    status: PAR_STATUS
    publicly_published: bool
    prefer_public: bool
    justification: str
    allowed_orgs_request_text: str
    allowed_orgs: list[str] | None
    denial_reason: str

    @classmethod
    def get_model_api(cls) -> type[MarketplaceDemoPublishAccessRecordEndpointAPI]: ...
    @property
    def model_api(self) -> MarketplaceDemoPublishAccessRecordEndpointAPI: ...
    def approve(
        self,
        *,
        publicly_published: bool = ...,
        allowed_orgs: list[str] = ...,
        **kwargs: Any,
    ) -> MarketplaceDemoPublishAccessRecord:
        """Approve this request.

        See ``MarketplaceDemoPublishAccessRecordEndpointAPI.approve``.
        """
        ...

    def deny(
        self,
        *,
        denial_reason: str = ...,
        **kwargs: Any,
    ) -> MarketplaceDemoPublishAccessRecord:
        """Deny this request.

        See ``MarketplaceDemoPublishAccessRecordEndpointAPI.deny``.
        """
        ...

    def set_visibility(
        self,
        *,
        publicly_published: bool,
        allowed_orgs: list[str] = ...,
        publish_images: bool = ...,
        **kwargs: Any,
    ) -> MarketplaceDemoPublishAccessRecord:
        """Set visibility.

        See ``MarketplaceDemoPublishAccessRecordEndpointAPI.set_visibility``.
        """
        ...

class MarketplaceDemoPublishAccessRecordEndpointAPI(
    BaseEndpointAPI[MarketplaceDemoPublishAccessRecord]
):
    """Endpoint API for managing marketplace demo publish access records.

    Provides methods for listing and retrieving records, plus admin actions
    to approve, deny, or change the visibility of a pending request.
    Records are created automatically by the Air platform when a publish
    or visibility-change request is submitted — they cannot be created via
    the SDK.
    """

    API_PATH: str
    API_APPROVE_PATH: str
    API_DENY_PATH: str
    API_SET_VISIBILITY_PATH: str
    model: type[MarketplaceDemoPublishAccessRecord]

    def list(  # type: ignore[override]
        self,
        *,
        marketplace_demo: str | PrimaryKey = ...,
        status: PAR_STATUS = ...,
        publicly_published: bool = ...,
        requested_by_email: str = ...,
        requesting_org_display_name: str = ...,
        requesting_org_ngc_org_name: str = ...,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
    ) -> Iterator[MarketplaceDemoPublishAccessRecord]:
        """List marketplace demo publish access records.

        Args:
            marketplace_demo: Filter by marketplace demo UUID
            status: Filter by request status
            publicly_published: Filter by public vs restricted visibility
            requested_by_email: Filter by requester email (case-insensitive)
            requesting_org_display_name: Filter by org display name (case-insensitive)
            requesting_org_ngc_org_name: Filter by org NGC name (case-insensitive)
            limit: Number of results to return per page
            offset: Initial index from which to return results
            ordering: Order by field (prefix with ``-`` for descending)
            search: Search query

        Returns:
            Iterator of MarketplaceDemoPublishAccessRecord instances

        Example:
            >>> records = api.marketplace_demo_publish_access_records
            >>> for record in records.list(status='PENDING'):
            ...     print(record.marketplace_demo_name, record.requested_by)
        """
        ...

    def get(self, pk: PrimaryKey, **kwargs: Any) -> MarketplaceDemoPublishAccessRecord:
        """Retrieve a specific publish access record.

        Args:
            pk: Record UUID
            **kwargs: Additional query parameters

        Returns:
            MarketplaceDemoPublishAccessRecord instance

        Example:
            >>> record = api.marketplace_demo_publish_access_records.get('record-uuid')
            >>> print(record.status, record.marketplace_demo_name)
        """
        ...

    def approve(
        self,
        *,
        record: MarketplaceDemoPublishAccessRecord | PrimaryKey,
        publicly_published: bool = ...,
        allowed_orgs: List[str] = ...,
        **kwargs: Any,
    ) -> MarketplaceDemoPublishAccessRecord:
        """Approve a pending publish access request.

        Args:
            record: The record to approve (instance or UUID)
            publicly_published: Whether to make the marketplace demo publicly accessible.
                When False, access is restricted to ``allowed_orgs``.
            allowed_orgs: List of org UUIDs that may access the marketplace demo.
                Only meaningful when ``publicly_published`` is False.
            **kwargs: Additional parameters

        Returns:
            Updated MarketplaceDemoPublishAccessRecord with status ``APPROVED``

        Example:
            >>> record = api.marketplace_demo_publish_access_records.get('record-uuid')
            >>> api.marketplace_demo_publish_access_records.approve(record=record)

            >>> # Approve with explicit visibility
            >>> api.marketplace_demo_publish_access_records.approve(
            ...     record=record,
            ...     publicly_published=True,
            ... )
        """
        ...

    def deny(
        self,
        *,
        record: MarketplaceDemoPublishAccessRecord | PrimaryKey,
        denial_reason: str = ...,
        **kwargs: Any,
    ) -> MarketplaceDemoPublishAccessRecord:
        """Deny a pending publish access request.

        Args:
            record: The record to deny (instance or UUID)
            denial_reason: Human-readable explanation of why the request
                was denied
            **kwargs: Additional parameters

        Returns:
            Updated MarketplaceDemoPublishAccessRecord with status ``DENIED``

        Example:
            >>> api.marketplace_demo_publish_access_records.deny(
            ...     record='record-uuid',
            ...     denial_reason='Does not meet publishing requirements.',
            ... )
        """
        ...

    def set_visibility(
        self,
        *,
        record: MarketplaceDemoPublishAccessRecord | PrimaryKey,
        publicly_published: bool,
        allowed_orgs: List[str] = ...,
        publish_images: bool = ...,
        **kwargs: Any,
    ) -> MarketplaceDemoPublishAccessRecord:
        """Update the visibility of a published marketplace demo.

        Args:
            record: The record to update (instance or UUID)
            publicly_published: Whether the marketplace demo should be publicly
                accessible. When False, access is restricted to ``allowed_orgs``.
            allowed_orgs: List of org UUIDs that may access the marketplace demo.
                Only meaningful when ``publicly_published`` is False.
            publish_images: When True, also publish referenced images owned by the
                demo's organization that do not cover the demo's target audience.
                Defaults to False.
            **kwargs: Additional parameters

        Returns:
            Updated MarketplaceDemoPublishAccessRecord

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
        ...
