# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from http import HTTPStatus
from pathlib import Path
from typing import Any, Optional, Union

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc import BaseCompatMixin, ImageCompatMixin
from air_sdk.bc.image import ImageEndpointAPICompatMixin
from air_sdk.bc.utils import _caller_stacklevel
from air_sdk.const import MAX_RECOMMENDED_UPLOAD_WORKERS
from air_sdk.endpoints import mixins
from air_sdk.helpers import image_upload
from air_sdk.utils import (
    join_urls,
    raise_if_invalid_response,
    validate_payload_types,
)


@dataclass
class MinimumResources:
    cpu: int
    memory: int
    storage: int


@dataclass(eq=False)
class ImageShare(AirModel):
    """Represents a shared image in the Air platform."""

    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    image: Image = field(metadata=AirModel.FIELD_FOREIGN_KEY)
    image_name: str
    image_version: str
    source_org_display_name: str
    target_org_display_name: str
    target_org: str = field(repr=False)
    expires_at: datetime
    claimed_by: str = field(repr=False)
    state: str

    @classmethod
    def get_model_api(cls) -> type['ImageShareEndpointAPI']:
        """Returns the respective `AirModelAPI` type for this model"""
        return ImageShareEndpointAPI

    @property
    def model_api(self) -> 'ImageShareEndpointAPI':
        """The current model API instance."""
        return self.get_model_api()(self.__api__)


@dataclass(eq=False)
class Image(BaseCompatMixin, ImageCompatMixin, AirModel):
    """Image model representing a network image.

    Attributes:
        id: Unique identifier for the image
        name: Human-readable name of the image
        version: Version of the image
        created: Timestamp when the image was created
        creator: User who created the image
        modified: Timestamp when the image was last modified
        mountpoint: Mountpoint of the image
        minimum_resources: Minimum resources required to run the image
        includes_air_agent: Whether the image includes the Air agent
        cpu_arch: CPU architecture of the image
        default_username: Default username for the image
        default_password: Default password for the image
        emulation_type: The types of emulation the image supports
        emulation_version: The version of the emulation the image supports
        provider: Provider of the image
        published: Whether the image is published
        publicly_published: Whether a published image is publicly accessible
        upload_status: Status of the image upload
        last_uploaded_at: Timestamp when the image was last uploaded
        size: Size of the image
        hash: Hash of the image
        is_owned_by_client: Whether the image is owned by the client
        notes: Notes about the image
        release_notes: Release notes for the image
        user_manual: User manual for the image
        publish_access_record_id: UUID of the active publish access record, or None
    """

    # Basic fields
    id: str = field(repr=False)
    name: str
    created: datetime = field(repr=False)
    creator: str | None = field(repr=False)
    modified: datetime = field(repr=False)
    # Configuration fields
    published: bool = field(repr=False)
    publicly_published: bool = field(repr=False)
    includes_air_agent: bool = field(repr=False)
    cpu_arch: str = field(repr=False)
    default_username: str = field(repr=False)
    default_password: str = field(repr=False)
    version: str
    mountpoint: str | None = field(repr=False)
    emulation_type: list[str] = field(repr=False)
    emulation_version: str = field(repr=False)
    provider: str = field(repr=False)
    minimum_resources: MinimumResources = field(repr=False)
    is_owned_by_client: bool = field(repr=False)
    notes: str | None = field(repr=False)
    release_notes: str | None = field(repr=False)
    user_manual: str | None = field(repr=False)
    # Upload fields
    upload_status: str
    last_uploaded_at: Union[datetime, None] = field(repr=False)
    size: int = field(repr=False)
    hash: str = field(repr=False)
    # Publishing fields
    publish_access_record_id: str | None = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type[ImageEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return ImageEndpointAPI

    @property
    def model_api(self) -> ImageEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    def upload_v3(
        self,
        *,
        filepath: str | Path,
        timeout: Optional[timedelta] = None,
        max_workers: int = 1,
        **kwargs: Any,
    ) -> Image:
        """Upload the image to the Air platform.

        All uploads use multipart upload to S3. Parts are ~100MB each,
        calculated automatically by the API.

        Example:
            >>> image.upload(filepath='local_file_path')
        """
        return self.model_api.upload_v3(
            image=self,
            filepath=filepath,
            timeout=timeout,
            max_workers=max_workers,
            **kwargs,
        )

    def clear_upload(self, **kwargs: Any) -> Image:
        """Clear the upload status of the image.

        Example:
            >>> image.clear_upload()
        """
        return self.model_api.clear_upload(image=self, **kwargs)

    def publish_v3(self, **kwargs: Any) -> Image:
        """Publish the image.

        Example:
            >>> image.publish()
            >>> image.publish(name='new-name', version='1.0.0')
        """
        return self.model_api.publish_v3(image=self, **kwargs)

    def unpublish(self, **kwargs: Any) -> Image:
        """Unpublish the image.

        Example:
            >>> image.unpublish()
            >>> image.unpublish(name='new-name', version='1.0.0')
        """
        return self.model_api.unpublish(image=self, **kwargs)

    def request_publish(self, **kwargs: Any) -> Image:
        """Submit a request to publish this image.

        Example:
            >>> image.request_publish(justification='Ready for community use')
        """
        return self.model_api.request_publish(image=self, **kwargs)

    def request_unpublish(self, **kwargs: Any) -> Image:
        """Submit a request to unpublish this image.

        Example:
            >>> image.request_unpublish(justification='No longer maintained')
        """
        return self.model_api.request_unpublish(image=self, **kwargs)

    def request_public(self, **kwargs: Any) -> Image:
        """Submit a request to change image visibility to public or restricted.

        Example:
            >>> image.request_public(prefer_public=True, justification='Open source')
        """
        return self.model_api.request_public(image=self, **kwargs)

    def request_allowlist_change(self, **kwargs: Any) -> Image:
        """Submit a request to change the allowlist for this image.

        Example:
            >>> image.request_allowlist_change(
            ...     justification='Add partner orgs',
            ...     allowed_orgs_request_text='org-a, org-b',
            ... )
        """
        return self.model_api.request_allowlist_change(image=self, **kwargs)

    def cancel_publish_access_record(self, **kwargs: Any) -> Image:
        """Cancel the active publish access record for this image.

        Example:
            >>> image.cancel_publish_access_record()
        """
        return self.model_api.cancel_publish_access_record(image=self, **kwargs)

    def share(self, *, target_org: str, **kwargs: Any) -> ImageShare:
        """Share the image with another organization.

        Example:
            >>> share = image.share(target_org='target-org-name')
        """
        return self.model_api.share(image=self, target_org=target_org, **kwargs)


class ImageEndpointAPI(
    ImageEndpointAPICompatMixin,
    mixins.ListApiMixin[Image],
    mixins.CreateApiMixin[Image],
    mixins.GetApiMixin[Image],
    mixins.PatchApiMixin[Image],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Image],
):
    """API client for image endpoints."""

    API_PATH = 'images'
    API_CLEAR_UPLOAD_PATH = 'clear-upload'
    API_PUBLISH_PATH = 'publish'
    API_UNPUBLISH_PATH = 'unpublish'
    API_REQUEST_PUBLISH_PATH = 'request-publish'
    API_REQUEST_UNPUBLISH_PATH = 'request-unpublish'
    API_REQUEST_PUBLIC_PATH = 'request-public'
    API_REQUEST_ALLOWLIST_CHANGE_PATH = 'request-allowlist-change'
    API_CANCEL_PUBLISH_ACCESS_RECORD_PATH = 'cancel-publish-access-record'
    API_CLAIM_IMAGE_SHARE_PATH = 'claim-image-share'
    model = Image

    def create_v3(
        self,
        **kwargs: Any,
    ) -> Image:
        """Create a new image.

        Example:
            >>> # Create image without upload
            >>> api.images.create(
            ...     name='cumulus-vx-1.2.3',
            ...     version='1.0.0',
            ...     default_username='user',
            ...     default_password='password',
            ... )

            >>> # Create and upload image in single step
            >>> api.images.create(
            ...     name='cumulus-vx-1.2.3',
            ...     version='1.0.0',
            ...     default_username='user',
            ...     default_password='password',
            ...     filepath='./cumulus-vx.qcow2',
            ... )
        """
        # Extract upload-related parameters before creating the image
        filepath = kwargs.pop('filepath', None)
        timeout = kwargs.pop('timeout', None)
        max_workers = kwargs.pop('max_workers', 1)

        # Create the image (without upload parameters)
        # Call CreateApiMixin.create() directly to avoid BC layer recursion
        img = mixins.CreateApiMixin.create(self, **kwargs)

        # If filepath was provided, upload the image
        if filepath is not None:
            upload_kwargs = {'image': img, 'filepath': filepath}
            if timeout is not None:
                upload_kwargs['timeout'] = timeout
            if max_workers != 1:
                upload_kwargs['max_workers'] = max_workers
            return self.upload_v3(**upload_kwargs)
        return img

    @validate_payload_types
    def upload_v3(
        self,
        *,
        image: Image | PrimaryKey,
        filepath: str | Path,
        timeout: Optional[timedelta] = None,
        max_workers: int = 1,
        **kwargs: Any,
    ) -> Image:
        """Upload the image to the Air platform.

        All uploads use multipart upload to S3. Parts are ~100MB each,
        calculated automatically by the API.

        Example:
            >>> # File upload
            >>> image.upload(filepath='image.qcow2')

            >>> # Large file with parallel upload
            >>> image.upload(filepath='large.qcow2', max_workers=4)
        """
        # Convert PrimaryKey to Image at the start if needed
        if not isinstance(image, Image):
            image = self.get(image)  # Fetch the full Image object

        # Validate max_workers
        if max_workers < 1:
            raise ValueError(f'max_workers must be >= 1, got {max_workers}')
        if max_workers > MAX_RECOMMENDED_UPLOAD_WORKERS:
            warnings.warn(
                f'max_workers={max_workers} is very high and may overwhelm '
                f'network resources. Consider using 4-8 workers for optimal '
                f'performance.',
                stacklevel=_caller_stacklevel(),
            )

        # Validate file exists and is readable
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f'File not found: {filepath}')
        if not filepath.is_file():
            raise ValueError(f'Path is not a regular file: {filepath}')
        if not os.access(filepath, os.R_OK):
            raise PermissionError(f'File not readable: {filepath}')

        # All uploads use multipart upload to S3
        return image_upload.upload_image(
            api_client=self.__api__,
            base_url=self.url,
            image=image,
            filepath=filepath,
            timeout=timeout,
            max_workers=max_workers,
            **kwargs,
        )

    @validate_payload_types
    def clear_upload(self, *, image: Image | PrimaryKey, **kwargs: Any) -> Image:
        """Clear the upload status of the image.

        Example:
            >>> api.images.clear_upload(image)
        """
        image_id = image.id if isinstance(image, Image) else image
        clear_upload_url = join_urls(self.url, str(image_id), self.API_CLEAR_UPLOAD_PATH)
        clear_upload_response = self.__api__.client.patch(
            clear_upload_url, data=mixins.serialize_payload(kwargs)
        )
        raise_if_invalid_response(clear_upload_response, status_code=HTTPStatus.OK)
        if isinstance(image, Image):
            image.refresh()
        # If a PrimaryKey was passed, load the Image from the response
        return self.load_model(clear_upload_response.json())

    @validate_payload_types
    def publish_v3(self, *, image: Image | PrimaryKey, **kwargs: Any) -> Image:
        """Publish the image.

        Example:
            >>> api.images.publish(image=image)
        """
        return self._patch_resource_action(image, self.API_PUBLISH_PATH, **kwargs)

    @validate_payload_types
    def unpublish(self, *, image: Image | PrimaryKey, **kwargs: Any) -> Image:
        """Unpublish the image.

        Example:
            >>> api.images.unpublish(image)
            >>> api.images.unpublish(image, name='new-name', version='new-version')
        """
        return self._patch_resource_action(image, self.API_UNPUBLISH_PATH, **kwargs)

    @validate_payload_types
    def request_publish(self, *, image: Image | PrimaryKey, **kwargs: Any) -> Image:
        """Submit a request to publish an image.

        Example:
            >>> api.images.request_publish(image=image, justification='Ready')
        """
        return self._patch_resource_action(image, self.API_REQUEST_PUBLISH_PATH, **kwargs)

    @validate_payload_types
    def request_unpublish(self, *, image: Image | PrimaryKey, **kwargs: Any) -> Image:
        """Submit a request to unpublish an image.

        Example:
            >>> api.images.request_unpublish(image=image, justification='Deprecated')
        """
        return self._patch_resource_action(
            image, self.API_REQUEST_UNPUBLISH_PATH, **kwargs
        )

    @validate_payload_types
    def request_public(self, *, image: Image | PrimaryKey, **kwargs: Any) -> Image:
        """Submit a request to change image visibility to public or restricted.

        Example:
            >>> api.images.request_public(image=img, prefer_public=True, justification='')
        """
        return self._patch_resource_action(image, self.API_REQUEST_PUBLIC_PATH, **kwargs)

    @validate_payload_types
    def request_allowlist_change(
        self, *, image: Image | PrimaryKey, **kwargs: Any
    ) -> Image:
        """Submit a request to change the allowlist for an image.

        Example:
            >>> api.images.request_allowlist_change(
            ...     image=image,
            ...     justification='Add partner orgs',
            ...     allowed_orgs_request_text='org-a, org-b',
            ... )
        """
        return self._patch_resource_action(
            image, self.API_REQUEST_ALLOWLIST_CHANGE_PATH, **kwargs
        )

    @validate_payload_types
    def cancel_publish_access_record(
        self, *, image: Image | PrimaryKey, **kwargs: Any
    ) -> Image:
        """Cancel the active publish access record for an image.

        Example:
            >>> api.images.cancel_publish_access_record(image=image)
        """
        return self._patch_resource_action(
            image, self.API_CANCEL_PUBLISH_ACCESS_RECORD_PATH, **kwargs
        )

    @validate_payload_types
    def share(
        self, *, image: Image | PrimaryKey, target_org: str, **kwargs: Any
    ) -> ImageShare:
        """Share the image with another organization.

        Example:
            >>> share = api.images.share(image='image-id', target_org='target-org-name')
        """
        image_id = image.id if isinstance(image, Image) else image
        if isinstance(image, Image):
            image.refresh()
        return self.shares.create(image=image_id, target_org=target_org, **kwargs)

    @validate_payload_types
    def claim_image_share(self, *, image_share: PrimaryKey, **kwargs: Any) -> Image:
        """Claim a shared image into your organization.

        Example:
            >>> image = api.images.claim_image_share(image_share='share-id')
        """
        claim_share_url = join_urls(self.url, self.API_CLAIM_IMAGE_SHARE_PATH)
        payload = {'image_share': image_share, **kwargs}
        claim_share_response = self.__api__.client.post(
            claim_share_url, data=mixins.serialize_payload(payload)
        )
        raise_if_invalid_response(claim_share_response, status_code=HTTPStatus.CREATED)
        return self.load_model(claim_share_response.json())

    @property
    def shares(self) -> ImageShareEndpointAPI:
        """Access the image shares API.

        Example:
            >>> # List all shared images
            >>> for share in api.images.shares.list():
            ...     print(share.image_name)
        """
        return ImageShareEndpointAPI(self.__api__)


class ImageShareEndpointAPI(
    mixins.ListApiMixin[ImageShare],
    mixins.CreateApiMixin[ImageShare],
    mixins.GetApiMixin[ImageShare],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[ImageShare],
):
    API_PATH = 'images/shares'
    model = ImageShare
