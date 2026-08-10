# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, List

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.images import Image
from air_sdk.types import PAR_STATUS

@dataclass(eq=False)
class ImagePublishAccessRecord(AirModel):
    """Represents a request to publish or change the visibility of an image.

    Publish access records are created when an org requests to publish an image
    or change its visibility. An admin must review the request and either
    approve or deny it.

    Attributes:
        id: Unique identifier for the record
        created: Timestamp when the record was created
        modified: Timestamp when the record was last modified
        image: The image the request is for (foreign key — lazily resolved)
        image_name: Name of the image at the time of the request
        image_version: Version of the image at the time of the request
        requested_by: Email of the user who submitted the request, or None
        requested_at: When the current request was submitted, or None if cancelled
        requesting_org: Org's readable_name (display_name or ngc_org_name), or None
        requesting_org_display_name: Display name of the requesting org, or None
        requesting_org_ngc_org_name: NGC org name of the requesting org, or None
        reviewed_by: Email of the admin who reviewed the request, or None
        reviewed_at: When the request was last reviewed, or None if still pending
        status: Current status of the request
        publicly_published: Whether the image should be publicly accessible
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
    image: Image
    image_name: str
    image_version: str
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
    def get_model_api(cls) -> type[ImagePublishAccessRecordEndpointAPI]: ...
    @property
    def model_api(self) -> ImagePublishAccessRecordEndpointAPI: ...
    def approve(
        self,
        *,
        publicly_published: bool = ...,
        allowed_orgs: list[str] = ...,
        **kwargs: Any,
    ) -> ImagePublishAccessRecord:
        """Approve this request. See ``ImagePublishAccessRecordEndpointAPI.approve``."""
        ...

    def deny(
        self,
        *,
        denial_reason: str = ...,
        **kwargs: Any,
    ) -> ImagePublishAccessRecord:
        """Deny this request. See ``ImagePublishAccessRecordEndpointAPI.deny``."""
        ...

    def set_visibility(
        self,
        *,
        publicly_published: bool,
        allowed_orgs: list[str] = ...,
        **kwargs: Any,
    ) -> ImagePublishAccessRecord:
        """Set visibility. See ``ImagePublishAccessRecordEndpointAPI.set_visibility``."""
        ...

class ImagePublishAccessRecordEndpointAPI(BaseEndpointAPI[ImagePublishAccessRecord]):
    """Endpoint API for managing image publish access records.

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
    model: type[ImagePublishAccessRecord]

    def list(  # type: ignore[override]
        self,
        *,
        image: str | PrimaryKey = ...,
        status: PAR_STATUS = ...,
        publicly_published: bool = ...,
        requested_by_email: str = ...,
        requesting_org_display_name: str = ...,
        requesting_org_ngc_org_name: str = ...,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
    ) -> Iterator[ImagePublishAccessRecord]:
        """List image publish access records.

        Args:
            image: Filter by image UUID
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
            Iterator of ImagePublishAccessRecord instances

        Example:
            >>> for record in api.image_publish_access_records.list(status='PENDING'):
            ...     print(record.image_name, record.requested_by)
        """
        ...

    def get(self, pk: PrimaryKey, **kwargs: Any) -> ImagePublishAccessRecord:
        """Retrieve a specific publish access record.

        Args:
            pk: Record UUID
            **kwargs: Additional query parameters

        Returns:
            ImagePublishAccessRecord instance

        Example:
            >>> record = api.image_publish_access_records.get('record-uuid')
            >>> print(record.status, record.image_name)
        """
        ...

    def approve(
        self,
        *,
        record: ImagePublishAccessRecord | PrimaryKey,
        publicly_published: bool = ...,
        allowed_orgs: List[str] = ...,
        **kwargs: Any,
    ) -> ImagePublishAccessRecord:
        """Approve a pending publish access request.

        Args:
            record: The record to approve (instance or UUID)
            publicly_published: Whether to make the image publicly accessible.
                When False, access is restricted to ``allowed_orgs``.
            allowed_orgs: List of org UUIDs that may access the image.
                Only meaningful when ``publicly_published`` is False.
            **kwargs: Additional parameters

        Returns:
            Updated ImagePublishAccessRecord with status ``APPROVED``

        Example:
            >>> record = api.image_publish_access_records.get('record-uuid')
            >>> api.image_publish_access_records.approve(record=record)

            >>> # Approve with explicit visibility
            >>> api.image_publish_access_records.approve(
            ...     record=record,
            ...     publicly_published=True,
            ... )
        """
        ...

    def deny(
        self,
        *,
        record: ImagePublishAccessRecord | PrimaryKey,
        denial_reason: str = ...,
        **kwargs: Any,
    ) -> ImagePublishAccessRecord:
        """Deny a pending publish access request.

        Args:
            record: The record to deny (instance or UUID)
            denial_reason: Human-readable explanation of why the request
                was denied
            **kwargs: Additional parameters

        Returns:
            Updated ImagePublishAccessRecord with status ``DENIED``

        Example:
            >>> api.image_publish_access_records.deny(
            ...     record='record-uuid',
            ...     denial_reason='Does not meet publishing requirements.',
            ... )
        """
        ...

    def set_visibility(
        self,
        *,
        record: ImagePublishAccessRecord | PrimaryKey,
        publicly_published: bool,
        allowed_orgs: List[str] = ...,
        **kwargs: Any,
    ) -> ImagePublishAccessRecord:
        """Update the visibility of a published image.

        Args:
            record: The record to update (instance or UUID)
            publicly_published: Whether the image should be publicly accessible.
                When False, access is restricted to ``allowed_orgs``.
            allowed_orgs: List of org UUIDs that may access the image.
                Only meaningful when ``publicly_published`` is False.
            **kwargs: Additional parameters

        Returns:
            Updated ImagePublishAccessRecord

        Example:
            >>> # Make image public
            >>> api.image_publish_access_records.set_visibility(
            ...     record='record-uuid',
            ...     publicly_published=True,
            ... )

            >>> # Restrict to specific orgs
            >>> api.image_publish_access_records.set_visibility(
            ...     record='record-uuid',
            ...     publicly_published=False,
            ...     allowed_orgs=['org-uuid-1', 'org-uuid-2'],
            ... )
        """
        ...
