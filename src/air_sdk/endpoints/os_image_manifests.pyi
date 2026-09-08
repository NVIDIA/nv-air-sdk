# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.images import Image
from air_sdk.types import OSImageCapabilities, OSImageManifestPlatform

@dataclass(eq=False)
class OSImageManifest(AirModel):
    """An OS image manifest: the NOS metadata describing an image.

    Each manifest pins, per hardware model, the platform information and OS
    template versions that apply to that model. A manifest therefore ties one
    image to a specific set of `PlatformInformation` and `OSTemplate` records.

    Attributes:
        id: Unique identifier for the manifest
        created: Timestamp when the manifest was created
        modified: Timestamp when the manifest was last modified
        image: The image this manifest describes. Loaded on demand
        os_type: The OS type the image runs, used as the lookup key into
                 platform templates and platform information
        platforms: Pinned platforms keyed by hardware model name. Each value
                   carries `platform_information_version` and
                   `os_template_version` for that model
        capabilities: Capability flags. Key presence means the capability is
                      supported; The value carries capability-specific
                      configuration. Unknown keys are rejected by the API with a 400
        os_template_partition: Partition of the boot disk that rendered OS
                             template files are written into: a filesystem
                             label, or a device path when
                             prefixed with `/dev/`. `None` means files are
                             written into the partition named by the image
                             mountpoint
        creator: Username of the user who created the manifest
    """

    id: str
    created: datetime
    modified: datetime
    image: Image
    os_type: str
    platforms: dict[str, OSImageManifestPlatform]
    capabilities: OSImageCapabilities
    os_template_partition: str | None
    creator: str | None

    @classmethod
    def get_model_api(cls) -> type[OSImageManifestEndpointAPI]: ...
    @property
    def model_api(self) -> OSImageManifestEndpointAPI: ...
    def update(
        self,
        *,
        platforms: dict[str, OSImageManifestPlatform] = ...,
        capabilities: OSImageCapabilities = ...,
        os_template_partition: str | None = ...,
        **kwargs: Any,
    ) -> None:
        """Update the manifest's properties.

        `image` and `os_type` are set at creation and immutable thereafter, so
        neither can be updated here.

        Args:
            platforms: Replacement pinned platforms, keyed by hardware model
            capabilities: Replacement capability flags, keyed by capability name
            os_template_partition: Partition rendered OS template files are
                                 written into: a filesystem label or a
                                 `/dev/`-prefixed device path. `None` clears it,
                                 falling back to the image mountpoint
            **kwargs: Additional fields for future API compatibility

        Returns:
            None

        Example:
            >>> manifest.update(os_template_partition='/dev/sdb1')
        """
        ...

    def delete(self) -> None:
        """Delete this OS image manifest.

        Returns:
            None

        Example:
            >>> manifest.delete()
        """
        ...

class OSImageManifestEndpointAPI(BaseEndpointAPI[OSImageManifest]):
    """Endpoint API for managing OS image manifests.

    Provides listing, retrieval, creation, update, and deletion of the
    manifests that describe how an image maps onto hardware platforms.
    """

    API_PATH: str
    model: type[OSImageManifest]

    def list(
        self,
        *,
        image: Image | PrimaryKey = ...,
        os_type: str = ...,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
        **kwargs: Any,
    ) -> Iterator[OSImageManifest]:
        # fmt: off
        """List OS image manifests.

        Args:
            image: Filter by image instance or UUID
            os_type: Filter by OS type
            limit: Number of results to return per page
            offset: Initial index from which to return results
            ordering: Order by field (prefix with "-" for descending)
            search: Search across manifest fields
            **kwargs: Additional filter parameters

        Returns:
            Iterator of OSImageManifest instances

        Example:
            >>> for manifest in api.os_image_manifests.list(
            ...     os_type='cumulus-linux'
            ... ):
            ...     print(manifest.os_type, manifest.platforms)
        """
        ...
        # fmt: on
    def get(self, pk: PrimaryKey, **kwargs: Any) -> OSImageManifest:
        """Retrieve a specific OS image manifest.

        Args:
            pk: OS image manifest UUID
            **kwargs: Additional query parameters

        Returns:
            OSImageManifest instance

        Example:
            >>> manifest = api.os_image_manifests.get('manifest-uuid')
            >>> print(manifest.os_type)
        """
        ...

    def create(
        self,
        *,
        image: Image | PrimaryKey,
        os_type: str,
        platforms: dict[str, OSImageManifestPlatform] = ...,
        capabilities: OSImageCapabilities = ...,
        os_template_partition: str | None = ...,
        **kwargs: Any,
    ) -> OSImageManifest:
        """Create an OS image manifest.

        Args:
            image: The image this manifest describes, or its UUID. Set at
                   creation and immutable thereafter
            os_type: The OS type the image runs
            platforms: Pinned platforms keyed by hardware model name
            capabilities: Capability flags. Key presence means the capability
                          is supported; the value holds optional config.
                          Unknown keys are rejected by the API with a 400
            os_template_partition: Partition of the boot disk that rendered OS
                                 template files are written into: a filesystem
                                 label, or a device path when
                                 prefixed with `/dev/`. An empty string is
                                 rejected by the API with a 400. When unset,
                                 files are written into the partition named by
                                 the image mountpoint
            **kwargs: Additional fields for future API compatibility

        Returns:
            The created OSImageManifest instance

        Example:
            >>> manifest = api.os_image_manifests.create(
            ...     image='image-uuid',
            ...     os_type='cumulus-linux',
            ...     platforms={
            ...         'SN3700': {
            ...             'platform_information_version': '1.2',
            ...             'os_template_version': '5.9',
            ...         }
            ...     },
            ... )
        """
        ...

    def patch(
        self,
        pk: PrimaryKey,
        *,
        platforms: dict[str, OSImageManifestPlatform] = ...,
        capabilities: OSImageCapabilities = ...,
        os_template_partition: str | None = ...,
        **kwargs: Any,
    ) -> OSImageManifest:
        """Update individual fields of an OS image manifest.

        `image` and `os_type` are set at creation and immutable thereafter, so
        neither is accepted here.

        Args:
            pk: OS image manifest UUID
            platforms: Replacement pinned platforms, keyed by hardware model
            capabilities: Replacement capability flags, keyed by capability name
            os_template_partition: Partition rendered OS template files are
                                 written into: a filesystem label or a
                                 `/dev/`-prefixed device path. `None` clears it,
                                 falling back to the image mountpoint
            **kwargs: Additional fields for future API compatibility

        Returns:
            Updated OSImageManifest instance

        Example:
            >>> manifest = api.os_image_manifests.patch(  # fmt: skip
            ...     'manifest-uuid', os_template_partition='/dev/sdb1'
            ... )
        """
        ...

    def delete(self, pk: PrimaryKey, **kwargs: Any) -> None:
        """Delete an OS image manifest.

        Args:
            pk: OS image manifest UUID
            **kwargs: Additional parameters

        Returns:
            None

        Example:
            >>> api.os_image_manifests.delete('manifest-uuid')
        """
        ...
