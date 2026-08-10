# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints import mixins
from air_sdk.endpoints.images import Image
from air_sdk.utils import validate_payload_types


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

    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    image: Image = field(metadata=AirModel.FIELD_FOREIGN_KEY)
    image_name: str
    image_version: str
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
    def get_model_api(cls) -> type['ImagePublishAccessRecordEndpointAPI']:
        """Returns the respective `AirModelAPI` type for this model"""
        return ImagePublishAccessRecordEndpointAPI

    @property
    def model_api(self) -> 'ImagePublishAccessRecordEndpointAPI':
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    def approve(self, **kwargs: Any) -> 'ImagePublishAccessRecord':
        """Approve this request. See ``ImagePublishAccessRecordEndpointAPI.approve``."""
        return self.model_api.approve(record=self, **kwargs)

    def deny(self, **kwargs: Any) -> 'ImagePublishAccessRecord':
        """Deny this request. See ``ImagePublishAccessRecordEndpointAPI.deny``."""
        return self.model_api.deny(record=self, **kwargs)

    def set_visibility(self, **kwargs: Any) -> 'ImagePublishAccessRecord':
        """Set visibility. See ``ImagePublishAccessRecordEndpointAPI.set_visibility``."""
        return self.model_api.set_visibility(record=self, **kwargs)


class ImagePublishAccessRecordEndpointAPI(
    mixins.ListApiMixin[ImagePublishAccessRecord],
    mixins.GetApiMixin[ImagePublishAccessRecord],
    BaseEndpointAPI[ImagePublishAccessRecord],
):
    """Endpoint API for managing image publish access records.

    Provides methods for listing and retrieving records, plus admin actions
    to approve, deny, or change the visibility of a pending request.
    Records are created automatically by the Air platform when a publish
    or visibility-change request is submitted — they cannot be created via
    the SDK.
    """

    API_PATH = 'publishing/image-publish-access-records'
    API_APPROVE_PATH = 'approve'
    API_DENY_PATH = 'deny'
    API_SET_VISIBILITY_PATH = 'set-visibility'
    model = ImagePublishAccessRecord

    @validate_payload_types
    def approve(
        self, *, record: ImagePublishAccessRecord | PrimaryKey, **kwargs: Any
    ) -> ImagePublishAccessRecord:
        """Approve a pending publish access request.

        Example:
            >>> record = api.image_publish_access_records.get('record-uuid')
            >>> api.image_publish_access_records.approve(record=record)

            >>> # Approve with explicit visibility
            >>> api.image_publish_access_records.approve(
            ...     record=record,
            ...     publicly_published=True,
            ... )
        """
        return self._patch_resource_action(record, self.API_APPROVE_PATH, **kwargs)

    @validate_payload_types
    def deny(
        self, *, record: ImagePublishAccessRecord | PrimaryKey, **kwargs: Any
    ) -> ImagePublishAccessRecord:
        """Deny a pending publish access request.

        Example:
            >>> api.image_publish_access_records.deny(
            ...     record='record-uuid',
            ...     denial_reason='Does not meet publishing requirements.',
            ... )
        """
        return self._patch_resource_action(record, self.API_DENY_PATH, **kwargs)

    @validate_payload_types
    def set_visibility(
        self, *, record: ImagePublishAccessRecord | PrimaryKey, **kwargs: Any
    ) -> ImagePublishAccessRecord:
        """Update the visibility of a published image.

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
        return self._patch_resource_action(record, self.API_SET_VISIBILITY_PATH, **kwargs)
