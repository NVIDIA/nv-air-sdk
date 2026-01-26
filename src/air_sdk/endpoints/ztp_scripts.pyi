# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey

if TYPE_CHECKING:
    from air_sdk.endpoints.simulations import Simulation

@dataclass(eq=False)
class ZTPScript(AirModel):
    """A ZTP (Zero Touch Provisioning) script for a simulation.

    ZTPScript objects should not be created directly. Use
    `simulation.create_ztp_script(content='...')` instead.

    Note:
        When printed, the `content` field is truncated to 50 characters with newlines
        collapsed to avoid flooding console/logs with large scripts.
        Access the full content via `ztp_script.content`.

    Attributes:
        created: When the script was created.
        modified: When the script was last modified.
        content: The script content.
        simulation: The simulation this script belongs to.

    Examples:
        >>> # Create a ZTP script
        >>> content = '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING\\necho Hi'
        >>> ztp_script = simulation.create_ztp_script(content=content)

        >>> # Update the script
        >>> content = '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING\\necho "Updated!"'
        >>> ztp_script.update(content=content)

        >>> # Delete the script
        >>> ztp_script.delete()
        >>> print(simulation.ztp_script)
        None
    """

    created: datetime
    modified: datetime
    content: str
    simulation: Simulation

    @classmethod
    def get_model_api(cls) -> type[ZTPScriptEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        ...

    @property
    def model_api(self) -> ZTPScriptEndpointAPI:
        """The current model API instance."""
        ...

    def update(self, *, content: str) -> None:
        """Update the content of this ZTP script.

        Args:
            content: The new script content to use.

        Example:
            >>> ztp_script = simulation.ztp_script
            >>> content = '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING\\n'
            >>> content += 'echo "Updated script"'
            >>> ztp_script.update(content=content)
        """
        ...

    def delete(self) -> None:
        """Delete the instance.

        After deletion, accessing `simulation.ztp_script` will return `None`.

        Example:
            >>> ztp_script = simulation.ztp_script
            >>> ztp_script.delete()
            >>> print(simulation.ztp_script)
            None
        """
        ...

class ZTPScriptEndpointAPI(BaseEndpointAPI[ZTPScript]):
    """Retrieve, update, and delete ZTP scripts for simulations.

    ZTPScripts should be created during import or off of `Simulation` objects:

    Examples:
        >>> # Create a ZTP script
        >>> content = '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING\\necho "Hello!"'
        >>> simulation.create_ztp_script(content=content)
        <ZTPScript(content='#!/bin/bash...')>

        >>> # Get a ZTP script
        >>> ztp_script = api.ztp_scripts.get(simulation)
        >>> print(ztp_script.content)
        #!/bin/bash
        # CUMULUS-AUTOPROVISIONING
        echo "Hello!"

        >>> # Update a ZTP script
        >>> content = '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING\\necho "Updated!"'
        >>> api.ztp_scripts.patch(simulation, content=content)

        >>> # Delete a ZTP script
        >>> api.ztp_scripts.delete(simulation)
    """

    API_PATH: str
    model: type[ZTPScript]

    def get(self, *, simulation: Simulation | PrimaryKey) -> ZTPScript:
        """Get the ZTP script for the simulation if it exists.

        Args:
            simulation: The simulation object or simulation ID.

        Returns:
            The ZTP script for the simulation.

        Raises:
            AirUnexpectedResponse: If the simulation doesn't have a ZTP script.

        Example:
            >>> # Using simulation object
            >>> ztp_script = api.ztp_scripts.get(simulation)

            >>> # Using simulation ID
            >>> ztp_script = api.ztp_scripts.get('simulation-uuid')

            >>> print(ztp_script.content)
            #!/bin/bash
            # CUMULUS-AUTOPROVISIONING
            echo "Hello, world!"
        """
        ...

    def patch(self, *, simulation: Simulation | PrimaryKey, content: str) -> ZTPScript:
        """Update the content of the ZTPScript.

        Args:
            simulation: The simulation object or simulation ID.
            content: The new script content.

        Returns:
            The updated ZTP script.

        Examples:
            >>> # Using simulation object
            >>> with open('ztp_script.sh', 'r') as f:
            ...     content = f.read()
            >>> updated_script = api.ztp_scripts.patch(simulation, content=content)

            >>> # Using simulation ID
            >>> content = '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING\\necho Hi'
            >>> api.ztp_scripts.patch('simulation-uuid', content=content)
        """
        ...

    def update(self, *, simulation: Simulation | PrimaryKey, content: str) -> ZTPScript:
        """Update the content of the ZTPScript.

        This is an alias for `patch()` provided for consistency with other endpoints.

        Args:
            simulation: The simulation object or simulation ID.
            content: The new script content.

        Returns:
            The updated ZTP script.

        Examples:
            >>> # Using simulation object
            >>> content = '#!/bin/bash\\n# CUMULUS-AUTOPROVISIONING'
            >>> api.ztp_scripts.update(simulation=simulation, content=content)

            >>> # Using simulation ID
            >>> api.ztp_scripts.update(simulation='sim-id', content=content)
        """
        ...

    def delete(self, *, simulation: Simulation | PrimaryKey) -> None:
        """Delete the ZTP script for the simulation.

        After deletion, `simulation.ztp_script` will return `None`.

        Args:
            simulation: The simulation object or simulation ID.

        Examples:
            >>> # Using simulation object
            >>> api.ztp_scripts.delete(simulation)

            >>> # Using simulation ID
            >>> api.ztp_scripts.delete('simulation-uuid')

            >>> print(simulation.ztp_script)
            None
        """
        ...
