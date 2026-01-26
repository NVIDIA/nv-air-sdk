# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for images endpoint type hints.
"""

from dataclasses import _MISSING_TYPE, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, Literal

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
        upload_status: Status of the image upload
        last_uploaded_at: Timestamp when the image was last uploaded
        size: Size of the image
        hash: Hash of the image
        is_owned_by_client: Whether the image is owned by the client
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
    upload_status: str
    last_uploaded_at: datetime | None
    size: int
    hash: str
    is_owned_by_client: bool

    @classmethod
    def get_model_api(cls) -> type[ImageEndpointAPI]: ...
    @property
    def model_api(self) -> ImageEndpointAPI: ...
    def update(
        self,
        *,
        name: str | _MISSING_TYPE = ...,
        version: str | _MISSING_TYPE = ...,
        default_username: str | _MISSING_TYPE = ...,
        default_password: str | _MISSING_TYPE = ...,
        mountpoint: str | None | _MISSING_TYPE = ...,
        cpu_arch: str | _MISSING_TYPE = ...,
        includes_air_agent: bool | _MISSING_TYPE = ...,
        emulation_type: list[str] | _MISSING_TYPE = ...,
        emulation_version: str | _MISSING_TYPE = ...,
        provider: str | _MISSING_TYPE = ...,
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
        timeout: timedelta | None | _MISSING_TYPE = ...,
        max_workers: int | _MISSING_TYPE = ...,
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
        name: str | _MISSING_TYPE = ...,
        version: str | _MISSING_TYPE = ...,
    ) -> Image:
        """Publish the image.

        Args:
            name: new name of the image
            version: new version of the image

        Returns:
            Image: the published image instance

        Example
        -------
            >>> image.publish()
            >>> image.publish(name='new-name', version='1.0.0')
        """
        ...

    def unpublish(
        self, *, name: str | _MISSING_TYPE = ..., version: str | _MISSING_TYPE = ...
    ) -> Image:
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

    def share(
        self, *, target_org: str, expires_at: datetime | _MISSING_TYPE = ...
    ) -> ImageShare:
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
    model: type[Image]

    def create(
        self,
        *,
        name: str,
        version: str,
        default_username: str,
        default_password: str,
        mountpoint: str | None | _MISSING_TYPE = ...,
        cpu_arch: str | _MISSING_TYPE = ...,
        includes_air_agent: bool | _MISSING_TYPE = ...,
        emulation_type: list[str] | _MISSING_TYPE = ...,
        emulation_version: str | _MISSING_TYPE = ...,
        provider: str | _MISSING_TYPE = ...,
        filepath: str | Path | _MISSING_TYPE = ...,
        timeout: timedelta | None | _MISSING_TYPE = ...,
        max_workers: int | _MISSING_TYPE = ...,
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
        upload_status: Literal[
            'READY',
            'UPLOADING',
            'VALIDATING',
            'COMPLETED',
            'PUBLISHED',
            'UNPUBLISHED',
            'UNPUBLISHING',
            'COPYING_FROM_IMAGE_SHARE',
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
        timeout: timedelta | None | _MISSING_TYPE = ...,
        max_workers: int | _MISSING_TYPE = ...,
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
        name: str | _MISSING_TYPE = ...,
        version: str | _MISSING_TYPE = ...,
    ) -> Image:
        """Publish the image.

        Args:
        Required parameters:
            image: image to publish

        Optional Parameters:
            name: The name of the image
            version: The version of the image

        Returns:
            None

        Example
        -------
            >>> api.images.publish(image)
        """
        ...

    def unpublish(
        self,
        *,
        image: Image | PrimaryKey,
        name: str | _MISSING_TYPE = ...,
        version: str | _MISSING_TYPE = ...,
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

    def share(
        self,
        *,
        image: Image | PrimaryKey,
        target_org: str,
        expires_at: datetime | _MISSING_TYPE = ...,
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
        name: str | _MISSING_TYPE = ...,
        version: str | _MISSING_TYPE = ...,
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
        limit: int | _MISSING_TYPE = ...,
        offset: int | _MISSING_TYPE = ...,
        ordering: str | _MISSING_TYPE = ...,
        search: str | _MISSING_TYPE = ...,
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
        expires_at: datetime | _MISSING_TYPE = ...,
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
