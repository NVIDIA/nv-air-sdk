# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, List, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey

class _OSTemplateRenderFileRequired(TypedDict):
    """Required fields for OSTemplateRenderFile."""

    content: str

class OSTemplateRenderFile(_OSTemplateRenderFileRequired, total=False):
    """A single OS template render entry: file content plus POSIX metadata.

    Attributes:
        content: Template body, rendered with the merged vars/generate context
        owner: POSIX owner — user name or numeric uid. Defaults to `root`
        group: POSIX group — group name or numeric gid. Defaults to `root`
        mode: POSIX octal file mode. Defaults to `0644`
    """

    owner: str
    group: str
    mode: str

@dataclass(eq=False)
class OSTemplate(AirModel):
    """An OS template: the files injected into a node at boot.

    A template describes, for one OS type and version, which files to render
    onto the node and which variables feed that rendering. An
    `OSImageManifest` pins a specific template version per hardware model.

    Attributes:
        id: Unique identifier for the template
        created: Timestamp when the template was created
        modified: Timestamp when the template was last modified
        os_type: The OS type this template applies to
        os_template_version: Version of this template
        org: Organization owning the template
        render: Absolute POSIX path to render entry. Each value has a
                required `content` plus optional `owner`, `group` and `mode`
                (defaulting to root/root/0644)
        creator: Email of the user who created the template
        generate: Variable names mapped to generation strategies
        vars: Variable names the render templates reference, declared for
        upload-time verification. Must exactly match the variables used
        across the render bodies.

    """

    id: str
    created: datetime
    modified: datetime
    os_type: str
    os_template_version: str
    org: str
    render: dict[str, OSTemplateRenderFile]
    creator: str | None
    generate: dict[str, str]
    vars: list[str]

    @classmethod
    def get_model_api(cls) -> type[OSTemplateEndpointAPI]: ...
    @property
    def model_api(self) -> OSTemplateEndpointAPI: ...
    def delete(self) -> None:
        """Delete this OS template.

        Returns:
            None

        Example:
            >>> template.delete()
        """
        ...

class OSTemplateEndpointAPI(BaseEndpointAPI[OSTemplate]):
    """Endpoint API for managing OS templates.

    Provides listing, retrieval, creation, and deletion of the templates that
    define which files are rendered onto a booting node. The API does not
    support partial or full updates on this resource.
    """

    API_PATH: str
    model: type[OSTemplate]

    def list(
        self,
        *,
        os_type: str = ...,
        os_template_version: str = ...,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
        **kwargs: Any,
    ) -> Iterator[OSTemplate]:
        # fmt: off
        """List OS templates.

        Args:
            os_type: Filter by OS type
            os_template_version: Filter by template version
            limit: Number of results to return per page
            offset: Initial index from which to return results
            ordering: Order by field (prefix with "-" for descending)
            search: Search across template fields
            **kwargs: Additional filter parameters

        Returns:
            Iterator of OSTemplate instances

        Example:
            >>> for template in api.os_templates.list(os_type='cumulus-linux'):
            ...     print(template.os_template_version)
        """
        ...
        # fmt: on
    def get(self, pk: PrimaryKey, **kwargs: Any) -> OSTemplate:
        """Retrieve a specific OS template.

        Args:
            pk: OS template UUID
            **kwargs: Additional query parameters

        Returns:
            OSTemplate instance

        Example:
            >>> template = api.os_templates.get('template-uuid')
            >>> print(template.os_type, template.os_template_version)
        """
        ...

    def create(
        self,
        *,
        os_type: str,
        os_template_version: str,
        render: dict[str, OSTemplateRenderFile],
        generate: dict[str, str] = ...,
        vars: List[str] = ...,
        **kwargs: Any,
    ) -> OSTemplate:
        """Create an OS template.

        Args:
            os_type: The OS type this template applies to
            os_template_version: Version of this template
            render: Render entries keyed by absolute POSIX path. Each value
                    requires `content`; `owner`, `group` and `mode` are
                    optional and default to root/root/0644
            generate: Variable names mapped to generation strategies
            vars: Names of the variables this template expects
            **kwargs: Additional fields for future API compatibility

        Returns:
            The created OSTemplate instance

        Example:
            >>> template = api.os_templates.create(
            ...     os_type='cumulus-linux',
            ...     os_template_version='5.9',
            ...     render={
            ...         '/etc/hostname': {'content': '{{ hostname }}'},
            ...     },
            ...     vars=['hostname'],
            ... )
        """
        ...

    def delete(self, pk: PrimaryKey, **kwargs: Any) -> None:
        """Delete an OS template.

        Args:
            pk: OS template UUID
            **kwargs: Additional parameters

        Returns:
            None

        Example:
            >>> api.os_templates.delete('template-uuid')
        """
        ...
