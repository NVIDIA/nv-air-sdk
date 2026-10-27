# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.types import ZTPConfigs, ZTPConfigsUpdate

if TYPE_CHECKING:
    from air_sdk.endpoints.simulations import Simulation

@dataclass(eq=False)
class ZTPScript(AirModel):
    """The ZTP (Zero Touch Provisioning) configuration of a simulation.

    It holds one entry per OS type: a provisioning script for Cumulus and a ZTP
    JSON object for NVOS. A simulation can configure either one, or both.

    ZTPScript objects should not be created directly. Use
    `simulation.create_ztp_script(...)` instead.

    Note:
        When printed, the configured OS types are listed and `content` is truncated
        to 50 characters with newlines collapsed, to avoid flooding console/logs
        with large scripts. Access the full configuration via
        `ztp_script.ztp_configs`.

    Attributes:
        created: When the configuration was created.
        modified: When the configuration was last modified.
        content: The Cumulus provisioning script, or None when Cumulus is not
                 configured.
        ztp_configs: The configuration keyed by OS type: `cumulus` holds the
                     provisioning script and `nvos` the ZTP JSON object. Object keys are
                     returned sorted by name. None when the Air API does not support
                     per-OS ZTP configuration.
        simulation: The simulation this configuration belongs to.

    Examples:
        >>> # Configure Cumulus and NVOS
        >>> ztp_script = simulation.create_ztp_script(
        ...     ztp_configs={
        ...         'cumulus': '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING\\necho Hi',
        ...         'nvos': {'ztp': {'01-image': {'uninstall': True}}},
        ...     }
        ... )

        >>> # Read one OS type
        >>> nvos_config = ztp_script.ztp_configs['nvos']

        >>> # Replace the NVOS configuration; the Cumulus script is kept
        >>> new_nvos_config = {'ztp': {'01-image': {'uninstall': False}}}
        >>> ztp_script.update(ztp_configs={'nvos': new_nvos_config})

        >>> # Remove the NVOS configuration only
        >>> ztp_script.update(ztp_configs={'nvos': None})

        >>> # Delete the whole configuration
        >>> simulation.delete_ztp_script()
        >>> print(simulation.ztp_script)
        None
    """

    created: datetime
    modified: datetime
    content: str | None
    ztp_configs: ZTPConfigs | None
    simulation: Simulation

    @classmethod
    def get_model_api(cls) -> type[ZTPScriptEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        ...

    @property
    def model_api(self) -> ZTPScriptEndpointAPI:
        """The current model API instance."""
        ...

    def update(
        self,
        *,
        content: str = ...,
        ztp_configs: ZTPConfigs | ZTPConfigsUpdate | dict[str, Any] = ...,
    ) -> None:
        """Update this ZTP configuration.

        Send either `content` or `ztp_configs`, not both. Only the OS types sent
        are written; the others are kept. Each OS type sent replaces its whole
        configuration, with nothing merged inside it: to change one NVOS
        section, send the complete NVOS configuration. An OS type set to `None`
        is removed; removing the last one needs `delete()`.

        Args:
            content: The new Cumulus provisioning script.
            ztp_configs: The new configuration of each OS type sent, keyed by OS
                         type: `cumulus` (the provisioning script) or `nvos` (the
                         ZTP JSON object), or `None` to remove that OS type.

        Example:
            >>> ztp_script = simulation.ztp_script
            >>> content = '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING\\n'
            >>> content += 'echo "Updated script"'
            >>> ztp_script.update(content=content)

            >>> nvos_config = {'ztp': {'01-image': {'uninstall': True}}}
            >>> ztp_script.update(ztp_configs={'nvos': nvos_config})

            >>> # Remove the NVOS configuration; the Cumulus script is kept
            >>> ztp_script.update(ztp_configs={'nvos': None})
        """
        ...

    def delete(self) -> None:
        """Delete this ZTP configuration, including every OS type.

        After deletion, accessing `simulation.ztp_script` returns `None`. To
        remove one OS type and keep the others, set it to `None` with `update()`.

        Example:
            >>> ztp_script = simulation.ztp_script
            >>> ztp_script.delete()
            >>> print(simulation.ztp_script)
            None
        """
        ...

class ZTPScriptEndpointAPI(BaseEndpointAPI[ZTPScript]):
    """Create, retrieve, update, and delete the ZTP configuration of simulations.

    A ZTP configuration can also be created during import or off of `Simulation`
    objects.

    `update()` and `patch()` here don't refresh a `simulation.ztp_script` read
    earlier: use `simulation.update_ztp_script()`, or call
    `simulation.clear_cached_property('ztp_script')` before reading it again.

    Examples:
        >>> # Add a ZTP configuration
        >>> ztp_script = api.ztp_scripts.create(
        ...     simulation=simulation,
        ...     content='#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING\\necho "Hello!"',
        ... )

        >>> # Get a ZTP configuration
        >>> ztp_script = api.ztp_scripts.get(simulation=simulation)
        >>> print(ztp_script.content)
        #!/bin/bash
        # CUMULUS-AUTOPROVISIONING
        echo "Hello!"

        >>> # Add an NVOS configuration; the Cumulus script is kept
        >>> api.ztp_scripts.patch(
        ...     simulation=simulation,
        ...     ztp_configs={'nvos': {'ztp': {'01-image': {'uninstall': True}}}},
        ... )

        >>> # Remove the NVOS configuration, then delete the rest
        >>> api.ztp_scripts.patch(simulation=simulation, ztp_configs={'nvos': None})
        >>> api.ztp_scripts.delete(simulation=simulation)
    """

    API_PATH: str
    model: type[ZTPScript]

    def create(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        content: str = ...,
        ztp_configs: ZTPConfigs | dict[str, Any] = ...,
    ) -> ZTPScript:
        """Add a ZTP configuration to a simulation that has none.

        Send either `content` or `ztp_configs`, not both. The simulation must be
        in the `INACTIVE` state.

        Args:
            simulation: The simulation object or simulation ID.
            content: The Cumulus provisioning script.
            ztp_configs: The configuration keyed by OS type: `cumulus` (the
                         provisioning script) and/or `nvos` (the ZTP JSON object).

        Returns:
            The created ZTP configuration.

        Raises:
            AirUnexpectedResponse: If the simulation already has a ZTP
                                   configuration; use `update()` to change it.

        Example:
            >>> api.ztp_scripts.create(
            ...     simulation='simulation-uuid',
            ...     ztp_configs={'nvos': {'ztp': {'01-image': {'uninstall': True}}}},
            ... )
        """
        ...

    def get(self, *, simulation: Simulation | PrimaryKey) -> ZTPScript:
        """Get the ZTP configuration for the simulation if it exists.

        Args:
            simulation: The simulation object or simulation ID.

        Returns:
            The ZTP configuration for the simulation.

        Raises:
            AirUnexpectedResponse: If the simulation doesn't have a ZTP
                                   configuration.

        Example:
            >>> # Using simulation object
            >>> ztp_script = api.ztp_scripts.get(simulation=simulation)

            >>> # Using simulation ID
            >>> ztp_script = api.ztp_scripts.get(simulation='simulation-uuid')

            >>> print(ztp_script.content)
            #!/bin/bash
            # CUMULUS-AUTOPROVISIONING
            echo "Hello, world!"
        """
        ...

    def patch(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        content: str = ...,
        ztp_configs: ZTPConfigs | ZTPConfigsUpdate | dict[str, Any] = ...,
    ) -> ZTPScript:
        """Update the ZTP configuration of a simulation.

        Send either `content` or `ztp_configs`, not both. Only the OS types sent
        are written; the others are kept. Each OS type sent replaces its whole
        configuration, with nothing merged inside it: to change one NVOS
        section, send the complete NVOS configuration. An OS type set to `None`
        is removed; removing the last one needs `delete()`. The simulation must
        be in the `INACTIVE` state.

        Args:
            simulation: The simulation object or simulation ID.
            content: The new Cumulus provisioning script.
            ztp_configs: The new configuration of each OS type sent, keyed by OS
                         type: `cumulus` (the provisioning script) or `nvos` (the
                         ZTP JSON object), or `None` to remove that OS type.

        Returns:
            The updated ZTP configuration.

        Examples:
            >>> # Using simulation object
            >>> with open('ztp_script.sh', 'r') as f:
            ...     content = f.read()
            >>> script = api.ztp_scripts.patch(simulation=simulation, content=content)

            >>> # Using simulation ID
            >>> api.ztp_scripts.patch(
            ...     simulation='simulation-uuid',
            ...     ztp_configs={'nvos': {'ztp': {'01-image': {'uninstall': True}}}},
            ... )
        """
        ...

    def update(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        content: str = ...,
        ztp_configs: ZTPConfigs | ZTPConfigsUpdate | dict[str, Any] = ...,
    ) -> ZTPScript:
        """Update the ZTP configuration of a simulation.

        This is an alias for `patch()` provided for consistency with other
        endpoints.

        Args:
            simulation: The simulation object or simulation ID.
            content: The new Cumulus provisioning script.
            ztp_configs: The new configuration of each OS type sent, keyed by OS
                         type: `cumulus` (the provisioning script) or `nvos` (the
                         ZTP JSON object), or `None` to remove that OS type.

        Returns:
            The updated ZTP configuration.

        Examples:
            >>> # Using simulation object
            >>> content = '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING'
            >>> api.ztp_scripts.update(simulation=simulation, content=content)

            >>> # Using simulation ID
            >>> api.ztp_scripts.update(
            ...     simulation='simulation-uuid',
            ...     ztp_configs={'nvos': {'ztp': {'01-image': {'uninstall': True}}}},
            ... )
        """
        ...

    def delete(self, *, simulation: Simulation | PrimaryKey) -> None:
        """Delete the ZTP configuration of a simulation, including every OS type.

        After deletion, `simulation.ztp_script` returns `None`. To remove one OS
        type and keep the others, set it to `None` with `update()`.

        Args:
            simulation: The simulation object or simulation ID.

        Examples:
            >>> # Using simulation object
            >>> api.ztp_scripts.delete(simulation=simulation)

            >>> # Using simulation ID
            >>> api.ztp_scripts.delete(simulation='simulation-uuid')

            >>> print(simulation.ztp_script)
            None
        """
        ...
