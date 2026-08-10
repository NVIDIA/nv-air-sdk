# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for images endpoint type hints.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, List, Literal

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey

@dataclass
class MinimumResources:
    cpu: int
    memory: int
    storage: int

@dataclass(eq=False)
class ImageShare(AirModel):
    id: str
    created: datetime
    modified: datetime
    image: Image  # Foreign key - lazily loads the Image object
    image_name: str
    image_version: str
    source_org_display_name: str
    target_org_display_name: str
    target_org: str
    expires_at: datetime
    claimed_by: str
    state: str

    @classmethod
    def get_model_api(cls) -> type[ImageShareEndpointAPI]: ...
    @property
    def model_api(self) -> ImageShareEndpointAPI: ...

@dataclass(eq=False)
class Image(AirModel):
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

    id: str
    name: str
    version: str
    created: datetime
    creator: str
    modified: datetime
    mountpoint: str | None
    minimum_resources: MinimumResources
    includes_air_agent: bool
    cpu_arch: str
    default_username: str
    default_password: str
    emulation_type: list[str]
    emulation_version: str
    provider: str
    published: bool
    publicly_published: bool
    upload_status: str
    last_uploaded_at: datetime | None
    size: int
    hash: str
    is_owned_by_client: bool
    notes: str | None
    release_notes: str | None
    user_manual: str | None
    publish_access_record_id: str | None

    @classmethod
    def get_model_api(cls) -> type[ImageEndpointAPI]: ...
    @property
    def model_api(self) -> ImageEndpointAPI: ...
    def update(
        self,
        *,
        name: str = ...,
        version: str = ...,
        default_username: str = ...,
        default_password: str = ...,
        mountpoint: str | None = ...,
        cpu_arch: str = ...,
        includes_air_agent: bool = ...,
        emulation_type: list[str] = ...,
        emulation_version: str = ...,
        provider: str = ...,
        notes: str | None = ...,
        release_notes: str | None = ...,
        user_manual: str | None = ...,
    ) -> None:
        """Update the image's properties.

        Args:
            name: Name of the image
            version: Version of the image
            default_username: Default username for the image
            default_password: Default password for the image
            mountpoint: Mountpoint of the image
            cpu_arch: CPU architecture of the image
            includes_air_agent: Whether the image includes the Air agent
            emulation_type: The types of emulation the image supports
            emulation_version: The version of the emulation the image supports
            provider: Provider of the image
            notes: Notes about the image
            release_notes: Release notes for the image
            user_manual: User manual for the image

        Example
        -------
            >>> image.update(name='new-name', version='1.0.0')
            >>> image.update(default_username='user', default_password='pass')
        """
        ...

    def upload(
        self,
        *,
        filepath: str | Path,
        timeout: timedelta | None = ...,
        max_workers: int = ...,
    ) -> Image:
        """Upload the image to the Air platform.

        All uploads use multipart upload to S3. Parts are ~100MB each,
        calculated automatically by the API.

        Args:
            filepath: local file path to the image
            timeout: Timeout per part upload (default: DEFAULT_UPLOAD_TIMEOUT).
            max_workers: number of concurrent workers for parallel uploads
                (default: 1 for sequential).

        Returns:
            Image: the uploaded image instance

        Example
        -------
            >>> image.upload(filepath='local_file_path')
        """
        ...

    def clear_upload(self) -> Image:
        """Clear the upload status of the image.

        Returns:
            Image: the image instance

        Example
        -------
            >>> image.clear_upload()
        """
        ...

    def publish(
        self,
        *,
        name: str = ...,
        version: str = ...,
        prefer_public: bool = ...,
        allowed_orgs: list[str] = ...,
        justification: str = ...,
    ) -> Image:
        """Publish the image.

        Args:
            name: new name of the image
            version: new version of the image
            prefer_public: whether to make the image publicly accessible
            allowed_orgs: list of org UUIDs to allowlist when not public
            justification: audit text describing the publish reason

        Returns:
            Image: the published image instance

        Example
        -------
            >>> image.publish()
            >>> image.publish(name='new-name', version='1.0.0')
        """
        ...

    def unpublish(self, *, name: str = ..., version: str = ...) -> Image:
        """Unpublish the image.

        Args:
            name: new name of the image
            version: new version of the image

        Returns:
            Image: the image instance

        Example
        -------
            >>> image.unpublish()
            >>> image.unpublish(name='new-name', version='1.0.0')
        """
        ...

    def request_publish(
        self,
        *,
        justification: str,
        prefer_public: bool = ...,
        allowed_orgs_request_text: str = ...,
        name: str = ...,
        version: str = ...,
    ) -> Image:
        """Submit a request to publish this image.

        Args:
            justification: Reason for requesting publication
            prefer_public: Whether to prefer public access over allowlist
            allowed_orgs_request_text: Free-text description of orgs to allowlist
            name: New name to apply on publish
            version: New version to apply on publish

        Returns:
            Image: the image instance with updated publish_access_record_id

        Example:
            >>> image.request_publish(justification='Ready for community use')
        """
        ...

    def request_unpublish(
        self,
        *,
        justification: str,
        name: str = ...,
        version: str = ...,
    ) -> Image:
        """Submit a request to unpublish this image.

        Args:
            justification: Reason for requesting unpublication
            name: New name to apply on unpublish
            version: New version to apply on unpublish

        Returns:
            Image: the image instance

        Example:
            >>> image.request_unpublish(justification='No longer maintained')
        """
        ...

    def request_public(
        self,
        *,
        prefer_public: bool,
        justification: str,
    ) -> Image:
        """Submit a request to change image visibility to public or restricted.

        Args:
            prefer_public: Whether to make the image publicly accessible
            justification: Reason for requesting the visibility change

        Returns:
            Image: the image instance

        Example:
            >>> image.request_public(prefer_public=True, justification='Open source')
        """
        ...

    def request_allowlist_change(
        self,
        *,
        justification: str,
        allowed_orgs_request_text: str,
    ) -> Image:
        """Submit a request to change the allowlist for this image.

        Args:
            justification: Reason for requesting the allowlist change
            allowed_orgs_request_text: Free-text description of orgs to allowlist

        Returns:
            Image: the image instance

        Example:
            >>> image.request_allowlist_change(
            ...     justification='Add partner orgs',
            ...     allowed_orgs_request_text='org-a, org-b',
            ... )
        """
        ...

    def cancel_publish_access_record(self) -> Image:
        """Cancel the active publish access record for this image.

        Returns:
            Image: the image instance

        Example:
            >>> image.cancel_publish_access_record()
        """
        ...

    def share(self, *, target_org: str, expires_at: datetime = ...) -> ImageShare:
        """Share the image with another organization.

        Args:
            target_org: The NGC org name of the organization receiving the image
            expires_at: The date and time the image share expires

        Returns:
            ImageShare: The created share instance

        Example
        -------
            >>> share = image.share(target_org='target-org-name')
        """
        ...

class ImageEndpointAPI(BaseEndpointAPI[Image]):
    """API client for image endpoints."""

    API_PATH: str
    API_CLEAR_UPLOAD_PATH: str
    API_PUBLISH_PATH: str
    API_UNPUBLISH_PATH: str
    API_REQUEST_PUBLISH_PATH: str
    API_REQUEST_UNPUBLISH_PATH: str
    API_REQUEST_PUBLIC_PATH: str
    API_REQUEST_ALLOWLIST_CHANGE_PATH: str
    API_CANCEL_PUBLISH_ACCESS_RECORD_PATH: str
    API_CLAIM_IMAGE_SHARE_PATH: str
    model: type[Image]

    def create(
        self,
        *,
        name: str,
        version: str,
        default_username: str,
        default_password: str,
        mountpoint: str | None = ...,
        cpu_arch: str = ...,
        includes_air_agent: bool = ...,
        emulation_type: list[str] = ...,
        emulation_version: str = ...,
        provider: str = ...,
        filepath: str | Path = ...,
        timeout: timedelta | None = ...,
        max_workers: int = ...,
    ) -> Image:
        """Create a new image.

        Args:
            name: Name of the image
            version: Version of the image
            default_username: Default username for the image
            default_password: Default password for the image
            mountpoint: Mountpoint of the image
            cpu_arch: CPU architecture of the image
            includes_air_agent: Whether the image includes the Air agent
            emulation_type: The types of emulation the image supports
            emulation_version: The version of the emulation the image supports
            provider: Provider of the image
            filepath: Optional path to image file. If provided, uploads the image
                after creation using upload.
            timeout: Timeout per part upload (default: DEFAULT_UPLOAD_TIMEOUT).
                Only used if filepath is provided.
            max_workers: Number of concurrent workers for parallel uploads
                (default: 1). Only used if filepath is provided.

        Returns:
            The created Image instance

        Example
        -------
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

            >>> # Create and upload with parallel workers
            >>> api.images.create(
            ...     name='cumulus-vx-1.2.3',
            ...     version='1.0.0',
            ...     default_username='user',
            ...     default_password='password',
            ...     filepath='./large-image.qcow2',
            ...     max_workers=4,
            ... )
        """
        ...

    def list(  # type: ignore[override]
        self,
        *,
        name: str = ...,
        version: str = ...,
        cpu_arch: Literal['x86', 'ARM'] = ...,
        creator: str = ...,
        includes_air_agent: bool = ...,
        provider: Literal['VM', 'CONTAINER'] = ...,
        published: bool = ...,
        publicly_published: bool = ...,
        upload_status: Literal[
            'READY',
            'UPLOADING',
            'VALIDATING',
            'COMPLETE',
            'PUBLISHING',
            'UNPUBLISHING',
            'COPYING_FROM_IMAGE_SHARE',
            'PENDING_PUBLISH',
            'PENDING_UNPUBLISH',
        ] = ...,
        hash: str = ...,
        is_owned_by_client: bool = ...,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
    ) -> Iterator[Image]:
        """List all images with optional filtering.

        Args:
            name: Name of the image
            version: Version of the image
            cpu_arch: CPU architecture of the image
            creator: Creator of the image
            includes_air_agent: Whether the image includes the Air agent
            emulation_type: The types of emulation the image supports
            emulation_version: The version of the emulation the image supports
            provider: Provider of the image
            published: Whether the image is published
            publicly_published: Whether a published image is publicly accessible
            upload_status: Status of the image upload
            last_uploaded_at: Timestamp when the image was last uploaded
            hash: Hash of the image
            is_owned_by_client: Whether the image is owned by the client
            limit: Maximum number of results to return
            offset: Offset for pagination
            ordering: Ordering of the results
            search: Search query

        Returns:
            Iterator of Image instances

        Example
        -------
            >>> for image in api.images.list():
            ...     print(image.name)

            >>> # Filter by name
            >>> for image in api.images.list(search='image-name'):
            ...     print(image.name)

            >>> # Order by name descending
            >>> for image in api.images.list(ordering='-name'):
            ...     print(image.name)
        """
        ...

    def get(self, pk: PrimaryKey) -> Image:
        """Get a specific image by ID.

        Args:
            pk: The image ID (string or UUID)

        Returns:
            The Image instance

        Example
        -------
            >>> image = api.images.get('image-id')
        """
        ...

    def upload(
        self,
        *,
        image: Image | PrimaryKey,
        filepath: str | Path,
        timeout: timedelta | None = ...,
        max_workers: int = ...,
    ) -> Image:
        """Upload the image to the Air platform.

        All uploads use multipart upload to S3. Parts are ~100MB each,
        calculated automatically by the API.

        Args:
            image: Image instance or image ID
            filepath: Path to the file to upload
            timeout: Timeout per part upload (default: DEFAULT_UPLOAD_TIMEOUT).
                This timeout applies to EACH part upload (not total operation).
            max_workers: Number of concurrent workers for uploads.
                Default: 1 (sequential uploads). Set > 1 for parallel uploads.

        Returns:
            Updated Image instance

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If filepath is not a regular file or max_workers < 1
            PermissionError: If the file is not readable
            AirUnexpectedResponse: If upload fails or backend returns invalid data
            requests.RequestException: For network/HTTP errors

        Example
        -------
            >>> # File upload
            >>> image.upload(filepath='image.qcow2')

            >>> # Large file with parallel upload
            >>> image.upload(filepath='large.qcow2', max_workers=4)
        """
        ...

    def clear_upload(self, *, image: Image | PrimaryKey) -> None:
        """Clear the upload status of the image.

        Args:
            image: image to clear upload

        Returns:
            None

        Example
        -------
            >>> api.images.clear_upload(image)
        """
        ...

    def publish(
        self,
        *,
        image: Image | PrimaryKey,
        name: str = ...,
        version: str = ...,
        prefer_public: bool = ...,
        allowed_orgs: List[str] = ...,
        justification: str = ...,
    ) -> Image:
        """Publish the image.

        Args:
        Required parameters:
            image: image to publish (Image instance or image ID)

        Optional Parameters:
            name: The name of the image
            version: The version of the image
            prefer_public: whether to make the image publicly accessible
            allowed_orgs: list of org UUIDs to allowlist when not public
            justification: audit text describing the publish reason

        Returns:
            Image: the published image instance

        Example
        -------
            >>> api.images.publish(image=image)
        """
        ...

    def unpublish(
        self,
        *,
        image: Image | PrimaryKey,
        name: str = ...,
        version: str = ...,
    ) -> Image:
        """Unpublish the image.

        Args:
            image: image to unpublish (Image instance or image ID)
            name: new name of the image
            version: new version of the image

        Returns:
            Image: the unpublished image instance

        Example
        -------
            >>> api.images.unpublish(image)
            >>> api.images.unpublish(image, name='new-name', version='new-version')
        """
        ...

    def request_publish(
        self,
        *,
        image: Image | PrimaryKey,
        justification: str,
        prefer_public: bool = ...,
        allowed_orgs_request_text: str = ...,
        name: str = ...,
        version: str = ...,
    ) -> Image:
        """Submit a request to publish an image.

        Args:
        Required parameters:
            image: image to request publication for (Image instance or image ID)
            justification: Reason for requesting publication

        Optional parameters:
            prefer_public: Whether to prefer public access over allowlist
            allowed_orgs_request_text: Free-text description of orgs to allowlist
            name: New name to apply on publish
            version: New version to apply on publish

        Returns:
            Image: the image instance with updated publish_access_record_id

        Example:
            >>> api.images.request_publish(image=image, justification='Ready')
        """
        ...

    def request_unpublish(
        self,
        *,
        image: Image | PrimaryKey,
        justification: str,
        name: str = ...,
        version: str = ...,
    ) -> Image:
        """Submit a request to unpublish an image.

        Args:
        Required parameters:
            image: image to request unpublication for (Image instance or image ID)
            justification: Reason for requesting unpublication

        Optional parameters:
            name: New name to apply on unpublish
            version: New version to apply on unpublish

        Returns:
            Image: the image instance

        Example:
            >>> api.images.request_unpublish(image=image, justification='Deprecated')
        """
        ...

    def request_public(
        self,
        *,
        image: Image | PrimaryKey,
        prefer_public: bool,
        justification: str,
    ) -> Image:
        """Submit a request to change image visibility to public or restricted.

        Args:
        Required parameters:
            image: image to update (Image instance or image ID)
            prefer_public: Whether to make the image publicly accessible
            justification: Reason for requesting the visibility change

        Returns:
            Image: the image instance

        Example:
            >>> api.images.request_public(image=img, prefer_public=True, justification='')
        """
        ...

    def request_allowlist_change(
        self,
        *,
        image: Image | PrimaryKey,
        justification: str,
        allowed_orgs_request_text: str,
    ) -> Image:
        """Submit a request to change the allowlist for an image.

        Args:
        Required parameters:
            image: image to update (Image instance or image ID)
            justification: Reason for requesting the allowlist change
            allowed_orgs_request_text: Free-text description of orgs to allowlist

        Returns:
            Image: the image instance

        Example:
            >>> api.images.request_allowlist_change(
            ...     image=image,
            ...     justification='Add partner orgs',
            ...     allowed_orgs_request_text='org-a, org-b',
            ... )
        """
        ...

    def cancel_publish_access_record(
        self,
        *,
        image: Image | PrimaryKey,
    ) -> Image:
        """Cancel the active publish access record for an image.

        Args:
        Required parameters:
            image: image to cancel the record for (Image instance or image ID)

        Returns:
            Image: the image instance

        Example:
            >>> api.images.cancel_publish_access_record(image=image)
        """
        ...

    def share(
        self,
        *,
        image: Image | PrimaryKey,
        target_org: str,
        expires_at: datetime = ...,
    ) -> ImageShare:
        """Share the image with another organization.

        Args:
        Required parameters:
            image: The image to share (Image instance or image ID)
            target_org: The NGC org name of the organization receiving the image

        Optional parameters:
            expires_at: The date and time the image share expires

        Returns:
            ImageShare: The created share object

        Example
        -------
            >>> share = api.images.share(image='image-id', target_org='target-org-name')
        """
        ...

    def claim_image_share(
        self,
        *,
        image_share: PrimaryKey,
        name: str = ...,
        version: str = ...,
    ) -> Image:
        # fmt: off
        """Claim a shared image into your organization.

        Args:
            image_share: The share ID to claim (string or UUID)
            name: new name of the image
            version: new version of the image

        Returns:
            Image: The claimed image

        Example
        -------
            >>> image = api.images.claim_image_share(image_share='share-id')
            >>> image = api.images.claim_image_share(
            ...     image_share='share-id', name='new-name', version='1.0.0'
            ... )
        """
        ...
    # fmt: on
    @property
    def shares(self) -> ImageShareEndpointAPI:
        """Access the image shares API.

        Returns:
            ImageShareEndpointAPI: The API for managing image shares

        Example
        -------
            >>> # List all shared images
            >>> for share in api.images.shares.list():
            ...     print(share.image_name)

            >>> # Create a new share
            >>> share = api.images.shares.create(
            ...     image='image-id',
            ...     target_org='target-org-name',
            ... )

            >>> # Get a specific share
            >>> share = api.images.shares.get('share-id')

            >>> # Delete a share
            >>> api.images.shares.delete('share-id')
        """
        ...

class ImageShareEndpointAPI(BaseEndpointAPI[ImageShare]):
    """API client for shared image endpoints."""

    API_PATH: str
    model: type[ImageShare]

    def list(  # type: ignore[override]
        self,
        *,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
    ) -> Iterator[ImageShare]:
        """List all shared images.

        Args:
            limit: Maximum number of results to return
            offset: Offset for pagination
            ordering: Ordering of the results
            search: Search query

        Returns:
            Iterator of ImageShare instances

        Example
        -------
            >>> # List all shared images
            >>> for share in api.images.shares.list():
            ...     print(share.image_name)

            >>> # Filter by image name
            >>> for share in api.images.shares.list(search='image-name'):
            ...     print(share.image_name)

            >>> # Order by image name descending
            >>> for share in api.images.shares.list(ordering='-image_name'):
            ...     print(share.image_name)
        """
        ...

    def create(
        self,
        *,
        image: Image | PrimaryKey,
        target_org: str,
        expires_at: datetime = ...,
    ) -> ImageShare:
        # fmt: off
        """Create a new image share.

        Args:
            image: The image or image ID to share
            target_org: The NGC org name of the organization receiving the image
            expires_at: The date and time the image share expires

        Returns:
            ImageShare: The created image share instance

        Example
        -------
            >>> share = api.images.shares.create(
            ...     image='image-id', target_org='target-org-name'
            ... )
        """
        ...
    # fmt: on
    def get(self, pk: PrimaryKey) -> ImageShare:
        """Get a specific shared image by ID.

        Args:
            pk: The image share ID (string or UUID)

        Returns:
            The ImageShare instance

        Example
        -------
            >>> share = api.images.shares.get('share-id')
        """
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """Delete (unshare) an image share.

        Args:
            pk: The share ID to delete (string or UUID)

        Returns:
            None

        Example
        -------
            >>> api.images.shares.delete('share-id')
            >>> api.images.shares.delete(share.id)
        """
        ...
