# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from io import TextIOBase
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc import (
    BaseCompatMixin,
    UserConfigEndpointAPICompatMixin,
)
from air_sdk.endpoints import mixins
from air_sdk.utils import (
    validate_payload_types,
)

if TYPE_CHECKING:
    pass


@dataclass(eq=False)
class UserConfig(BaseCompatMixin, AirModel):
    id: str
    name: str
    kind: str
    content: str | None = field(default=None, metadata=AirModel.FIELD_LAZY, repr=False)

    # TODO: Add these fields once ResourceBudget endpoint is implemented in v3:
    # organization: str | None = field(repr=False)
    # organization_budget: ResourceBudget | None = field(
    #     metadata=AirModel.FIELD_FOREIGN_KEY, repr=False
    # )

    KIND_CLOUD_INIT_USER_DATA = 'cloud-init-user-data'
    KIND_CLOUD_INIT_META_DATA = 'cloud-init-meta-data'

    @classmethod
    def get_model_api(cls) -> type[UserConfigEndpointAPI]:
        return UserConfigEndpointAPI

    @property
    def model_api(self) -> UserConfigEndpointAPI:
        return self.get_model_api()(self.__api__)

    @validate_payload_types
    def update(self, **kwargs: Any) -> None:
        self._ensure_pk_exists('updated')
        self.model_api.update(user_config=self, **kwargs)
        self.refresh()


class UserConfigEndpointAPI(
    UserConfigEndpointAPICompatMixin,
    mixins.ListApiMixin[UserConfig],
    mixins.CreateApiMixin[UserConfig],
    mixins.GetApiMixin[UserConfig],
    mixins.PatchApiMixin[UserConfig],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[UserConfig],
):
    API_PATH = 'userconfigs'
    model = UserConfig

    @staticmethod
    def _resolve_user_config_content(content: Union[str, Path, TextIOBase]) -> str:
        """Resolve user config content from various input types.

        Args:
            content: Content as one of:
                - str: Literal content string (never interpreted as file path)
                - Path: File path to read from (must exist)
                - TextIOBase: File handle to read from

        Returns:
            Resolved content as string

        Raises:
            FileNotFoundError: If Path doesn't exist
            ValueError: If content type is not supported

        Examples:
            >>> # Literal string content
            >>> api.user_configs.create(content="#!/bin/bash\\necho 'hello'")

            >>> # Read from file (explicit Path object)
            >>> from pathlib import Path
            >>> api.user_configs.create(content=Path('/path/to/script.sh'))

            >>> # Read from file handle
            >>> with open('/path/to/script.sh') as f:
            ...     api.user_configs.create(content=f)
        """
        if isinstance(content, str):
            # String is always treated as literal content (never as file path)
            # This removes ambiguity - users must use Path() for file inputs
            return content
        elif isinstance(content, Path):
            with content.open('r') as content_file:
                return content_file.read()
        elif isinstance(content, TextIOBase):
            # File handle
            return content.read()
        else:
            raise ValueError(
                f'Unsupported content type: {type(content)}. '
                f'Expected str (literal content), Path (file path), or file handle.'
            )

    @validate_payload_types
    def create(self, **kwargs: Any) -> UserConfig:
        # Check for required parameters
        if 'name' not in kwargs:
            raise TypeError("create() missing required keyword argument: 'name'")
        if 'kind' not in kwargs:
            raise TypeError("create() missing required keyword argument: 'kind'")
        if 'content' not in kwargs:
            raise TypeError("create() missing required keyword argument: 'content'")

        # Resolve content from various input types
        content = kwargs.pop('content')
        resolved_content = self._resolve_user_config_content(content)

        payload = {
            'name': kwargs.pop('name'),
            'kind': kwargs.pop('kind'),
            'content': resolved_content,
            **kwargs,
        }
        return super().create(**payload)

    @validate_payload_types
    def patch(self, pk: PrimaryKey, **kwargs: Any) -> UserConfig:
        # Resolve content from various input types (string, Path, file handle)
        if 'content' in kwargs:
            kwargs['content'] = self._resolve_user_config_content(kwargs['content'])

        return super().patch(pk, **kwargs)  # type: ignore[no-any-return,misc]

    @validate_payload_types
    def update(
        self,
        *,
        user_config: UserConfig | PrimaryKey,
        **kwargs: Any,
    ) -> UserConfig:
        user_config_id = (
            user_config.id if isinstance(user_config, UserConfig) else user_config
        )
        return self.patch(user_config_id, **kwargs)
