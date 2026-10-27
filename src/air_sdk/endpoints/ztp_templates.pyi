# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey

@dataclass(eq=False)
class ZTPTemplate(AirModel):
    """A starting-point ZTP configuration, one per OS type.

    A template is example content offered in the ZTP editor, not a
    simulation's own configuration. Editing a template never changes any
    existing simulation. Templates are platform-wide rather than per
    organization, and `os_type` identifies the row in the URL.

    Attributes:
        id: Unique identifier for the template
        os_type: OS family this template applies to. It identifies the
                 template, so it cannot be changed: assigning another value
                 raises `AttributeError` and sends no request
        template: Template body. Cumulus holds a string containing the
                  provisioning script; NVOS holds a JSON object containing
                  the ZTP configuration. Object keys are returned sorted by
                  name, which for NVOS is the order the sections run in.
                  Array order is left as stored
        created: Timestamp when the template was created
        modified: Timestamp when the template was last modified
        created_by: UUID of the client that created the template, or None
                    for a seeded template or once that client is deleted
        last_modified_by: UUID of the client that created or last updated the
                          template, or None for a seeded template no client
                          has edited yet or once that client is deleted
    """

    id: str
    os_type: Literal['cumulus', 'nvos']
    template: str | dict[str, Any]
    created: datetime
    modified: datetime
    created_by: str | None
    last_modified_by: str | None

    @classmethod
    def get_model_api(cls) -> type[ZTPTemplateEndpointAPI]: ...
    @property
    def model_api(self) -> ZTPTemplateEndpointAPI: ...
    def update(
        self,
        *,
        template: str | dict[str, Any] = ...,
        **kwargs: Any,
    ) -> None:
        """Replace the body of this template.

        `os_type` identifies the template and cannot be changed; create a
        separate template to cover another OS type.

        Args:
            template: The new body. A string for Cumulus, a JSON object for
                      NVOS
            **kwargs: Additional fields for future API compatibility

        Example:
            >>> template.update(template='#!/bin/bash\\n#CUMULUS-AUTOPROVISIONING\\n')
        """
        ...

    def delete(self) -> None:
        """Delete this template.

        Simulations keep the ZTP configuration they already saved; only the
        starting point offered in the editor is removed. After deletion, the
        instance's `os_type` is set to None.

        Example:
            >>> template.delete()
        """
        ...

class ZTPTemplateEndpointAPI(BaseEndpointAPI[ZTPTemplate]):
    """Endpoint API for managing ZTP templates.

    Any client with an Air role can read a template. Creating, updating and
    deleting are restricted to Admin and SRE clients.
    """

    API_PATH: str
    model: type[ZTPTemplate]

    def get(self, pk: PrimaryKey, **params: Any) -> ZTPTemplate:
        """Retrieve the template for one OS type.

        Args:
            pk: The OS type identifying the template, e.g. `'cumulus'`
            **params: Additional query parameters

        Returns:
            The matching ZTPTemplate

        Example:
            >>> template = api.ztp_templates.get('cumulus')
        """
        ...

    def create(
        self,
        *,
        os_type: Literal['cumulus', 'nvos'],
        template: str | dict[str, Any],
        **kwargs: Any,
    ) -> ZTPTemplate:
        """Create the template for one OS type.

        Only one template may exist per OS type, and Air seeds a Cumulus and an
        NVOS template when it's deployed, so `create()` returns 400 while that
        OS type has a template. To change a template, use `patch()` or the
        template's `update()`.

        Args:
            os_type: OS family the template applies to
            template: The body. A string for Cumulus, a JSON object for NVOS
            **kwargs: Additional fields for future API compatibility

        Returns:
            The created ZTPTemplate

        Example:
            >>> # Works only when the OS type has no template
            >>> api.ztp_templates.create(
            ...     os_type='nvos',
            ...     template={'ztp': {'01-image': {'uninstall': True}}},
            ... )
        """
        ...

    def patch(
        self,
        pk: PrimaryKey,
        *,
        template: str | dict[str, Any] = ...,
        **kwargs: Any,
    ) -> ZTPTemplate:
        """Replace the body of the template for one OS type.

        Args:
            pk: The OS type identifying the template
            template: The new body
            **kwargs: Additional fields for future API compatibility

        Returns:
            The updated ZTPTemplate

        Example:
            >>> api.ztp_templates.patch(
            ...     'nvos',
            ...     template={'ztp': {'01-image': {'uninstall': True}}},
            ... )
        """
        ...

    def update(
        self,
        *,
        ztp_template: ZTPTemplate | PrimaryKey,
        template: str | dict[str, Any] = ...,
        **kwargs: Any,
    ) -> ZTPTemplate:
        """Replace the body of a template.

        Args:
            ztp_template: The template instance, or the OS type identifying it
            template: The new body
            **kwargs: Additional fields for future API compatibility

        Returns:
            The updated ZTPTemplate

        Example:
            >>> api.ztp_templates.update(
            ...     ztp_template='nvos',
            ...     template={'ztp': {'01-image': {'uninstall': True}}},
            ... )
        """
        ...

    def delete(self, pk: PrimaryKey, **kwargs: Any) -> None:
        """Delete the template for one OS type.

        Args:
            pk: The OS type identifying the template
            **kwargs: Additional parameters

        Example:
            >>> api.ztp_templates.delete('nvos')
        """
        ...
