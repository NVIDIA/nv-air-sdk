# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
    # Basic fields
    id: str = field(repr=False)
    name: str
    created: datetime = field(repr=False)
    creator: str | None = field(repr=False)
    modified: datetime = field(repr=False)
    # Configuration fields
    published: bool = field(repr=False)
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
    # Upload fields
    upload_status: str
    last_uploaded_at: Union[datetime, None] = field(repr=False)
    size: int = field(repr=False)
    hash: str = field(repr=False)

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
        return self.model_api.upload_v3(
            image=self,
            filepath=filepath,
            timeout=timeout,
            max_workers=max_workers,
            **kwargs,
        )

    def clear_upload(self, **kwargs: Any) -> Image:
        return self.model_api.clear_upload(image=self, **kwargs)

    def publish_v3(self, **kwargs: Any) -> Image:
        return self.model_api.publish_v3(image=self, **kwargs)

    def unpublish(self, **kwargs: Any) -> Image:
        return self.model_api.unpublish(image=self, **kwargs)

    def share(self, *, target_org: str, **kwargs: Any) -> ImageShare:
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
    API_PATH = 'images'
    model = Image

    def create_v3(
        self,
        **kwargs: Any,
    ) -> Image:
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
        """Upload an image file. See stub file for full documentation."""
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
                stacklevel=2,
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
        image_id = image.id if isinstance(image, Image) else image
        clear_upload_url = join_urls(self.url, str(image_id), 'clear-upload')
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
        image_id = image.id if isinstance(image, Image) else image
        publish_url = join_urls(self.url, str(image_id), 'publish')
        publish_response = self.__api__.client.patch(
            publish_url, data=mixins.serialize_payload(kwargs)
        )
        raise_if_invalid_response(publish_response, status_code=HTTPStatus.OK)
        if isinstance(image, Image):
            image.refresh()
        return self.load_model(publish_response.json())

    @validate_payload_types
    def unpublish(self, *, image: Image | PrimaryKey, **kwargs: Any) -> Image:
        image_id = image.id if isinstance(image, Image) else image
        unpublish_url = join_urls(self.url, str(image_id), 'unpublish')
        unpublish_response = self.__api__.client.patch(
            unpublish_url, data=mixins.serialize_payload(kwargs)
        )
        raise_if_invalid_response(unpublish_response, status_code=HTTPStatus.OK)
        if isinstance(image, Image):
            image.refresh()
        return self.load_model(unpublish_response.json())

    @validate_payload_types
    def share(
        self, *, image: Image | PrimaryKey, target_org: str, **kwargs: Any
    ) -> ImageShare:
        image_id = image.id if isinstance(image, Image) else image
        if isinstance(image, Image):
            image.refresh()
        return self.shares.create(image=image_id, target_org=target_org, **kwargs)

    @validate_payload_types
    def claim_image_share(self, *, image_share: PrimaryKey, **kwargs: Any) -> Image:
        claim_share_url = join_urls(self.url, 'claim-image-share')
        payload = {'image_share': image_share, **kwargs}
        claim_share_response = self.__api__.client.post(
            claim_share_url, data=mixins.serialize_payload(payload)
        )
        raise_if_invalid_response(claim_share_response, status_code=HTTPStatus.CREATED)
        return self.load_model(claim_share_response.json())

    @property
    def shares(self) -> ImageShareEndpointAPI:
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
