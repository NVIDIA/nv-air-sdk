# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for marketplace demo tags endpoint type hints.
"""

from dataclasses import _MISSING_TYPE, dataclass
from datetime import datetime
from typing import Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.marketplace_demos import MarketplaceDemoEndpointAPI

@dataclass(eq=False)
class MarketplaceDemoTag(AirModel):
    """Marketplace demo tag model representing a tag for marketplace demos.

    Attributes:
        id: Unique identifier for the tag
        name: Name of the tag
        is_public: Whether the tag is in the public marketplace catalog
        created: Timestamp when the tag was created
        modified: Timestamp when the tag was last modified
    """

    id: str
    name: str
    is_public: bool
    created: datetime
    modified: datetime

    @classmethod
    def get_model_api(cls) -> type[MarketplaceDemoTagEndpointAPI]: ...
    @property
    def model_api(self) -> MarketplaceDemoTagEndpointAPI: ...
    @property
    def marketplace_demos(self) -> MarketplaceDemoEndpointAPI:
        """Marketplace demos assigned this tag.

        Returns a marketplace demos endpoint pre-filtered to demos tagged with
        this tag's name.

        Example:
            >>> tag = api.marketplace_demo_tags.get('tag-id')
            >>> for demo in tag.marketplace_demos.list():
            ...     print(demo.name)
        """
        ...

class MarketplaceDemoTagEndpointAPI(BaseEndpointAPI[MarketplaceDemoTag]):
    """API client for marketplace demo tag endpoints."""

    API_PATH: str
    model: type[MarketplaceDemoTag]

    def create(
        self,
        *,
        name: str,
    ) -> MarketplaceDemoTag:
        """Create a new marketplace demo tag.

        Args:
            name: Name for the new tag

        Returns:
            The created MarketplaceDemoTag instance

        Example:
            >>> tag = api.marketplace_demo_tags.create(name='networking')
        """
        ...

    def list(  # type: ignore[override]
        self,
        *,
        is_public: bool | _MISSING_TYPE = ...,
        limit: int | _MISSING_TYPE = ...,
        offset: int | _MISSING_TYPE = ...,
        search: str | _MISSING_TYPE = ...,
        ordering: str | _MISSING_TYPE = ...,
    ) -> Iterator[MarketplaceDemoTag]:
        """List all marketplace demo tags.

        Optional parameters:
            is_public: Filter by whether the tag is in the public marketplace
                catalog (true) or org-scoped (false)
            limit: Number of results to return per page
            offset: The initial index from which to return the results
            search: Search term to filter tags
            ordering: Order the response by the specified field

        Returns:
            Iterator of MarketplaceDemoTag instances

        Example:
            >>> # List all tags
            >>> for tag in api.marketplace_demo_tags.list():
            ...     print(tag.name)
        """
        ...

    def get(self, pk: PrimaryKey) -> MarketplaceDemoTag:
        """Get a specific marketplace demo tag by ID.

        Args:
            pk: The tag ID (string or UUID)

        Returns:
            The MarketplaceDemoTag instance

        Example:
            >>> tag = api.marketplace_demo_tags.get('tag-id')
            >>> print(tag.name)
        """
        ...

    def patch(
        self,
        pk: PrimaryKey,
        *,
        name: str | _MISSING_TYPE = ...,
    ) -> MarketplaceDemoTag:
        """Update a marketplace demo tag.

        Args:
            pk: The tag ID (string or UUID)
            name: New name for the tag

        Returns:
            The updated MarketplaceDemoTag instance

        Example:
            >>> tag = api.marketplace_demo_tags.patch('tag-id', name='new-name')
        """
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """Delete a marketplace demo tag.

        Args:
            pk: The tag ID (string or UUID)

        Example:
            >>> api.marketplace_demo_tags.delete('tag-id')
        """
        ...
