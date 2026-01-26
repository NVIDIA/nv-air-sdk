# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for user_configs endpoint type hints.
"""

from dataclasses import dataclass
from io import TextIOBase
from pathlib import Path
from typing import Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc import BaseCompatMixin, UserConfigEndpointAPICompatMixin

@dataclass(eq=False)
class UserConfig(BaseCompatMixin, AirModel):
    """UserConfig model representing cloud-init configurations.

    The string representation shows: id, name, kind

    Attributes:
        id: Unique identifier for the user config
        name: Human-readable name of the user config
        kind: Type of cloud-init config (user-data or meta-data)
        content: The cloud-init script content (lazy-loaded)

    Constants:
        KIND_CLOUD_INIT_USER_DATA: Constant for user-data kind
        KIND_CLOUD_INIT_META_DATA: Constant for meta-data kind
    """

    id: str
    name: str
    kind: str
    content: str | None

    KIND_CLOUD_INIT_USER_DATA: str
    KIND_CLOUD_INIT_META_DATA: str

    @classmethod
    def get_model_api(cls) -> type[UserConfigEndpointAPI]: ...
    @property
    def model_api(self) -> UserConfigEndpointAPI: ...
    def update(self, *, name: str | None = ..., content: str | None = ...) -> None:
        """Update specific fields of the user config.

        Args:
            name: New name for the user config
            content: New cloud-init script content

        Example:
            >>> user_config = api.user_configs.get('config-id')
            >>> user_config.update(name='Updated Config')
            >>> user_config.update(content='#cloud-config\\n...')
        """
        ...

    def refresh(self) -> None:
        """Refresh the user config from the API, loading all fields including content.

        Example:
            >>> user_config.refresh()
            >>> print(user_config.content)
        """
        ...

    def delete(self) -> None:
        """Delete this user config from the system.

        Example:
            >>> user_config.delete()
        """
        ...

class UserConfigEndpointAPI(
    UserConfigEndpointAPICompatMixin, BaseEndpointAPI[UserConfig]
):
    """API interface for managing UserConfig resources.

    Provides methods for CRUD operations on user configs (cloud-init configurations).
    """

    API_PATH: str
    model: type[UserConfig]

    def list(  # type: ignore[override]
        self,
        *,
        kind: str | None = ...,
        limit: int | None = ...,
        offset: int | None = ...,
        ordering: str | None = ...,
        search: str | None = ...,
    ) -> Iterator[UserConfig]:
        # fmt: off
        """List user configs with optional filtering and pagination.

        Args:
            kind: Filter by config kind (user-data or meta-data)
            limit: Maximum number of results to return
            offset: Number of results to skip
            ordering: Field to order results by (prefix with '-' for descending)
            search: Search term to filter results

        Yields:
            UserConfig instances

        Example:
            >>> # List all user configs
            >>> for config in api.user_configs.list():
            ...     print(config.name)
            >>>
            >>> # Filter by kind
            >>> for config in api.user_configs.list(
            ...     kind=api.user_configs.model.KIND_CLOUD_INIT_USER_DATA
            ... ):
            ...     print(config.name)
            >>>
            >>> # Search with pagination
            >>> for config in api.user_configs.list(search='my-config', limit=10):
            ...     print(config.name)
        """
        # fmt: on
        ...

    def get(self, user_config: UserConfig | PrimaryKey) -> UserConfig:
        """Get a specific user config by ID.

        Args:
            user_config: UserConfig instance or ID string

        Returns:
            UserConfig instance with all fields populated

        Example:
            >>> config = api.user_configs.get('config-id-here')
            >>> print(config.content)
        """
        ...

    def create(
        self,
        *,
        name: str,
        kind: str,
        content: str | Path | TextIOBase,
    ) -> UserConfig:
        """Create a new user config.

        Args:
            name: Name for the user config
            kind: Type of config (use KIND_CLOUD_INIT_USER_DATA or
                KIND_CLOUD_INIT_META_DATA constants)
            content: Cloud-init script content. Can be provided as:
                - str: Raw content or file path
                - Path: Path object to a file
                - TextIOBase: Open file handle

        Returns:
            Newly created UserConfig instance

        Note:
            User configs are automatically associated with your default organization.
            The 'organization' parameter from v1/v2 has been removed in v3.

        Example:
            >>> # String content
            >>> config = api.user_configs.create(
            ...     name='my-user-data',
            ...     kind=api.user_configs.model.KIND_CLOUD_INIT_USER_DATA,
            ...     content='#cloud-config\\npackages:\\n  - vim\\n',
            ... )
            >>>
            >>> # File path
            >>> config = api.user_configs.create(
            ...     name='my-user-data',
            ...     kind='cloud-init-user-data',
            ...     content='/path/to/file.txt',
            ... )
            >>>
            >>> # Path object
            >>> from pathlib import Path
            >>> config = api.user_configs.create(
            ...     name='my-user-data',
            ...     kind='cloud-init-user-data',
            ...     content=Path('/path/to/file.txt'),
            ... )
        """
        ...

    def update(
        self,
        *,
        user_config: UserConfig | PrimaryKey,
        name: str | None = ...,
        content: str | Path | TextIOBase | None = ...,
    ) -> UserConfig:
        """Update a user config (patch operation).

        Args:
            user_config: UserConfig instance or ID string
            name: New name for the user config
            content: New cloud-init script content

        Returns:
            Updated UserConfig instance

        Example:
            >>> config = api.user_configs.update(
            ...     user_config='config-id',
            ...     name='New Name',
            ...     content='#cloud-config\\n...',
            ... )
        """
        ...

    def patch(
        self,
        pk: PrimaryKey,
        *,
        name: str | None = ...,
        content: str | Path | TextIOBase | None = ...,
    ) -> UserConfig:
        """Patch a user config with partial updates.

        Args:
            pk: UserConfig ID string
            name: New name for the user config
            content: New cloud-init script content

        Returns:
            Updated UserConfig instance

        Example:
            >>> config = api.user_configs.patch(
            ...     pk='config-id',
            ...     name='Updated Name',
            ... )
        """
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """Delete a user config.

        Args:
            pk: UserConfig ID string

        Example:
            >>> api.user_configs.delete('config-id')
        """
        ...
