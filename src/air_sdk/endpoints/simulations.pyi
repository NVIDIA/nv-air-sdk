# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for simulations endpoint type hints.
"""

from dataclasses import _MISSING_TYPE, dataclass
from datetime import datetime, timedelta
from io import TextIOBase
from pathlib import Path
from typing import Any, Iterator, List, Literal

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.history import History
from air_sdk.endpoints.interfaces import InterfaceEndpointAPI
from air_sdk.endpoints.node_instructions import NodeInstructionEndpointAPI
from air_sdk.endpoints.nodes import NodeEndpointAPI
from air_sdk.endpoints.services import Service, ServiceEndpointAPI
from air_sdk.endpoints.ztp_scripts import ZTPScript
from air_sdk.types import NodeAssignmentDataV3, NodeRebuildPayload, NodeResetPayload

@dataclass(eq=False)
class Simulation(AirModel):
    """Simulation model representing a network simulation.

    The string representation shows: id, name, state, creator

    Attributes:
        id: Unique identifier for the simulation
        name: Human-readable name of the simulation
        created: Timestamp when the simulation was created
        modified: Timestamp when the simulation was last modified
        state: Current state of the simulation (see Literal values for all states)
        creator: Email of the user who created the simulation
        auto_oob_enabled: Whether automatic out-of-band management is enabled
        disable_auto_oob_dhcp: Whether DHCP should be disabled on the OOB server
        auto_netq_enabled: Whether automatic NetQ is enabled
        sleep_at: When the simulation should be automatically put to sleep (stored)
        expires_at: When the simulation should be automatically deleted
        documentation: Documentation markdown or URL to documentation markdown
        complete_checkpoint_count: Number of complete checkpoints in the simulation
    """

    id: str
    name: str
    created: datetime
    modified: datetime
    state: Literal[
        'CLONING',
        'CREATING',
        'IMPORTING',
        'INVALID',
        'INACTIVE',
        'REQUESTING',
        'PROVISIONING',
        'PREPARE_BOOT',
        'BOOTING',
        'ACTIVE',
        'PREPARE_SHUTDOWN',
        'SHUTTING_DOWN',
        'SAVING',
        'PREPARE_REBUILD',
        'REBUILDING',
        'DELETING',
        'PREPARE_PURGE',
        'PURGING',
        'DEMO',
        'TRAINING',
    ]
    creator: str
    auto_oob_enabled: bool | None
    disable_auto_oob_dhcp: bool | None
    auto_netq_enabled: bool | None
    sleep_at: datetime | None
    expires_at: datetime | None
    documentation: str | None
    complete_checkpoint_count: int

    @classmethod
    def get_model_api(cls) -> type[SimulationEndpointAPI]: ...
    @property
    def model_api(self) -> SimulationEndpointAPI: ...
    def update(
        self,
        *,
        name: str | _MISSING_TYPE = ...,
        sleep_at: datetime | None | _MISSING_TYPE = ...,
        expires_at: datetime | None | _MISSING_TYPE = ...,
        documentation: str | None | _MISSING_TYPE = ...,
    ) -> None:
        """Update the simulation's properties.

        Note: For OOB, DHCP and NetQ configuration, use dedicated methods like
        enable_auto_oob(), disable_auto_oob(),
        enable_auto_netq(), disable_auto_netq(), etc.

        Args:
            name: New name for the simulation
            sleep_at: When the simulation should be automatically put to sleep
            expires_at: When the simulation should be automatically deleted
            documentation: Documentation markdown or URL to documentation markdown

        Example:
            >>> simulation.update(name='New Name', documentation='https://docs.example.com')
        """
        ...

    def enable_auto_oob(self, disable_auto_oob_dhcp: bool = ...) -> None:
        """Enable automatic Out-of-band management for this simulation.

        Args:
            disable_auto_oob_dhcp: If True, disable DHCP on the OOB management network


        Example:
            # Enable OOB  with DHCP:
            >>> simulation.enable_auto_oob()

            # Enable OOB without DHCP:
            >>> simulation.enable_auto_oob(disable_auto_oob_dhcp=True)
        """
        ...

    def disable_auto_oob(self) -> None:
        """Disable automatic Out-of-band management for this simulation.

        Example:
            >>> simulation.disable_auto_oob()
        """
        ...

    def enable_auto_netq(self) -> None:
        """Enable automatic NetQ for this simulation.

        Example:
            >>> simulation.enable_auto_netq()
        """
        ...

    def disable_auto_netq(self) -> None:
        """Disable automatic NetQ for this simulation.

        Example:
            >>> simulation.disable_auto_netq()
        """
        ...

    def start(self, *, checkpoint: str | None = ...) -> None:
        """Start the simulation.

        Args:
            checkpoint: Optional checkpoint ID to start from.
                       If not specified, the API will use its default behavior
                       (typically uses the most recent checkpoint if available).
                       If explicitly set to None, starts from clean state (rebuild).
                       If a string, starts from the specified checkpoint.

        Example:
            # Normal start (API determines behavior):
            >>> simulation.start()

            # Start from specific checkpoint:
            >>> simulation.start(checkpoint='checkpoint-id')

            # Rebuild (start from clean state, no checkpoint):
            >>> simulation.start(checkpoint=None)
        """
        ...

    def shutdown(self, *, create_checkpoint: bool = ...) -> None:
        """Shut down the simulation.

        Args:
            create_checkpoint: Whether to create a checkpoint before shutting down.
                              If not specified, the API will use its default behavior.

        Example:
            # Normal shutdown (API determines behavior):
            >>> simulation.shutdown()

            # Explicitly create checkpoint before shutdown:
            >>> simulation.shutdown(create_checkpoint=True)

            # Explicitly don't create checkpoint:
            >>> simulation.shutdown(create_checkpoint=False)
        """
        ...

    def rebuild(self, *, checkpoint: str | None = ...) -> None:
        """Rebuild the simulation from a given checkpoint.

        Tears down the simulation and starts it from the given checkpoint.
        If no checkpoint is provided, the simulation will be rebuilt from the clean state.

        Args:
            checkpoint: Optional checkpoint ID to rebuild from.
                        If not specified, the API will use its default behavior
                        (the current checkpoint the simulation is running off of).
                        If explicitly set to None, starts from clean state (rebuild).
                        If a string, starts from the specified checkpoint.

        Example:
            # Rebuild simulation from specific checkpoint:
            >>> simulation.rebuild(checkpoint='checkpoint-id')
        """
        ...

    def wait_for_state(
        self,
        target_states: str | list[str],
        timeout: timedelta | None = None,
        poll_interval: timedelta | None = None,
        error_states: str | list[str] | None = None,
    ) -> None:
        # fmt: off
        """Wait for simulation to reach one of the target states.

        Args:
            target_states: Single state or list of states to wait for
            timeout: Maximum time to wait (default: 120 seconds)
            poll_interval: Time between status checks (default: 2 seconds)
            error_states: Single state or list of states that should raise an error

        Raises:
            ValueError: If the simulation enters one of the error states
            TimeoutError: If timeout is reached before target state

        Example:
            >>> simulation.wait_for_state('ACTIVE', error_states=['INVALID'])
            
            >>> # Wait for multiple possible states
            >>> simulation.wait_for_state(['INACTIVE', 'ACTIVE'])
            
            >>> # Custom timeout
            >>> simulation.wait_for_state(
            ...     'ACTIVE',
            ...     timeout=timedelta(minutes=5),
            ...     error_states=['INVALID', 'DELETING']
            ... )
        """
        ...
    # fmt: on
    def set_sleep_time(self, sleep_at: datetime | None) -> None:
        """Set when the simulation should be automatically put to sleep (stored).

        Accepts any timezone-aware datetime, which will be automatically
        converted to UTC. Naive datetimes (without timezone) will trigger
        a warning and assume local timezone.

        Args:
            sleep_at: Timezone-aware datetime when simulation should sleep,
                     or None to clear. Naive datetimes will assume local
                     timezone and emit a warning.

        Example:
            >>> from datetime import datetime, timedelta, timezone

            # Timezone-aware datetime (recommended):
            >>> sleep_time = datetime.now(timezone.utc) + timedelta(hours=1)
            >>> simulation.set_sleep_time(sleep_time)

            # Naive datetime (triggers warning):
            >>> now = datetime.now()
            >>> simulation.set_sleep_time(now + timedelta(hours=1))

            # Clear sleep time:
            >>> simulation.set_sleep_time(None)
        """
        ...

    def set_expire_time(self, expires_at: datetime | None) -> None:
        """Set when the simulation should be automatically deleted.

        Accepts any timezone-aware datetime, which will be automatically
        converted to UTC. Naive datetimes (without timezone) will trigger
        a warning and assume local timezone.

        Args:
            expires_at: Timezone-aware datetime when simulation should expire,
                       or None to clear. Naive datetimes will assume local
                       timezone and emit a warning.

        Example:
            >>> from datetime import datetime, timedelta, timezone

            # Timezone-aware datetime (recommended):
            >>> expire_time = datetime.now(timezone.utc) + timedelta(hours=2)
            >>> simulation.set_expire_time(expire_time)

            # Naive datetime (triggers warning):
            >>> now = datetime.now()
            >>> simulation.set_expire_time(now + timedelta(hours=2))

            # Clear expiration time:
            >>> simulation.set_expire_time(None)
        """
        ...

    def create_ztp_script(self, *, content: str) -> ZTPScript:
        # fmt: off
        """Create a ZTP (Zero Touch Provisioning) script for the simulation.
        
        Args:
            content: The content of the ZTP script
            
        Returns:
            The created ZTPScript instance
            
        Example:
            >>> script = simulation.create_ztp_script(
            ...     content='#!/bin/bash\\n#CUMULUS-AUTOPROVISIONING\\necho "Hello World"'
            ... )
        """
        ...
        # fmt: on
    def update_ztp_script(self, *, content: str) -> ZTPScript:
        """Update the ZTP script for this simulation.

        Args:
            content: The new script content

        Returns:
            The updated ZTPScript instance

        Example:
            >>> updated_script = simulation.update_ztp_script(
            ...     content='#!/bin/bash\\n#CUMULUS-AUTOPROVISIONING\\necho "Updated"'
            ... )
        """
        ...

    def delete_ztp_script(self) -> None:
        """Delete the ZTP script for this simulation.

        After deletion, simulation.ztp_script will return None.

        Example:
            >>> simulation.delete_ztp_script()
            >>> print(simulation.ztp_script)
            None
        """
        ...

    def export(
        self,
        *,
        image_ids: bool = ...,
        topology_format: Literal['JSON'] = 'JSON',
    ) -> dict[str, Any]:
        """Export the simulation.

        Args:
            image_ids: Whether to include image IDs in the export.
                      If not specified, the API will use its default behavior.
            topology_format: Format for the topology in the export.
                            If not specified, the API will use its default behavior.

        Returns:
            Dictionary containing the exported simulation data

        Example:
            # Export with API defaults:
            >>> export_data = simulation.export()

            # Export with specific options:
            >>> export_data = simulation.export(image_ids=True, topology_format='JSON')
        """
        ...

    def clone(
        self, *, checkpoint: str | None = ..., attempt_start: bool = ...
    ) -> Simulation:
        """Clone/duplicate the simulation.

        Args:
            checkpoint: Optional checkpoint ID to clone from. If not specified,
                       Air will find the most recent COMPLETE checkpoint if it exists.
            attempt_start: If the simulation should start immediately after cloning

        Returns:
            The cloned Simulation instance

        Example:
            # Simple clone:
            >>> cloned_sim = simulation.clone()

            # Clone with specific checkpoint:
            >>> cloned_sim = simulation.clone(checkpoint='checkpoint-id')

            # Clone and start immediately:
            >>> cloned_sim = simulation.clone(attempt_start=True)
        """
        ...

    @property
    def ztp_script(self) -> ZTPScript | None:
        """Get the simulation's ZTP script if it exists.

        Returns:
            The ZTPScript instance or None if no script exists

        Example:
            >>> if script := simulation.ztp_script:
            ...     print(script.content)
        """
        ...

    def get_history(
        self,
        *,
        category: str = ...,
        actor: str = ...,
        search: str = ...,
        ordering: Literal[
            'actor', 'category', 'created', 'model', 'object_id', 'description'
        ] = ...,
    ) -> Iterator[History]:
        """Get the historical entries for the simulation.

        Args:
            category: Filter by category of the history entries
            actor: Filter by actor who performed the actions
            search: Search term to filter the history entries
            ordering: Order the response by the specified field

        Returns:
            Iterator of History objects for the simulation

        Example:
            # Basic usage with ordering:
            >>> for history in simulation.get_history(ordering='created'):
            ...     print(history.description)

            # Search and filter:
            >>> for history in simulation.get_history(search='OOB', ordering='category'):
            ...     print(history.description)
        """
        ...

    @property
    def nodes(self) -> NodeEndpointAPI:
        """Query for the related nodes of the simulation.

        Returns:
            NodeEndpointAPI instance filtered for this simulation's nodes

        Example:
            >>> for node in simulation.nodes.list():
            ...     print(node.name)
        """
        ...

    @property
    def interfaces(self) -> InterfaceEndpointAPI:
        """Query for the related interfaces of the simulation.

        Returns:
            InterfaceEndpointAPI instance filtered for this simulation's interfaces

        Example:
            >>> for interface in simulation.interfaces.list():
            ...     print(interface.name)
        """
        ...

    @property
    def node_instructions(self) -> NodeInstructionEndpointAPI:
        """Query for the related node instructions of the simulation.

        Returns:
            NodeInstructionEndpointAPI filtered for this simulation's instructions

        Example:
            >>> for instruction in simulation.node_instructions.list():
            ...     print(instruction.name, instruction.state)
        """
        ...

    @property
    def services(self) -> ServiceEndpointAPI:
        # fmt: off
        """Query for the related services of the simulation.

        Returns:
            ServiceEndpointAPI instance filtered for this simulation's services

        Example:
            >>> for service in simulation.services.list():
            ...     print(f'{service.name}: {service.worker_fqdn}:{service.worker_port}')
            >>>
            >>> # Create service using 'node:interface' string (BC)
            >>> service = simulation.services.create(
            ...     name='SSH', interface='server-1:eth0', dest_port=22
            ... )
        """
        ...
    # fmt: on
    def create_service(
        self,
        *,
        node_name: str,
        interface_name: str,
        node_port: int,
        name: str = ...,
        service_type: Literal['SSH', 'HTTPS', 'HTTP', 'OTHER'] = ...,
    ) -> Service:
        # fmt: off
        """Create service using node and interface names.

        Args:
            node_name: Node name in this simulation
            interface_name: Interface name on the node (e.g., 'eth0', 'swp1')
            node_port: Port number on the node
            name: Service name (optional)
            service_type: Service type - 'SSH', 'HTTPS', 'HTTP', or 'OTHER'

        Returns:
            Service object

        Raises:
            ValueError: If node or interface not found in simulation

        Example:
            >>> service = sim.create_service(
            ...     node_name='server-1',
            ...     interface_name='eth0',
            ...     name='SSH Access',
            ...     node_port=22,
            ...     service_type='SSH'
            ... )
        """
        ...
        # fmt: on
    def node_bulk_assign(
        self,
        *,
        nodes: List[NodeAssignmentDataV3],
    ) -> None:
        """Bulk assign configurations to nodes in this simulation.

        Args:
            nodes: List of node assignment data containing node,
                        user_data, and meta_data

        Example:
            >>> # Bulk assign cloud-init configs to multiple nodes
            >>> simulation.node_bulk_assign(
            ...     nodes=[
            ...         {'node': 'node1', 'user_data': 'config1'},
            ...         {'node': 'node2', 'meta_data': 'config2'},
            ...     ],
            ... )
        """
        ...

    def node_bulk_reset(
        self,
        *,
        nodes: List[NodeResetPayload],
    ) -> None:
        """Reset specific nodes within this simulation.

        Resetting the node emulates the hardware reset button on physical machines
        where the machine is immediately restarted without a clean shutdown of the
        operating system. For nodes that are not currently running, this means simply
        booting them back up.

        Args:
            nodes: List of node reset payloads, each containing a node object or ID

        Example:
            >>> # Reset a single node
            >>> simulation.node_bulk_reset(nodes=[{'id': node.id}])

            >>> # Reset multiple nodes using node IDs
            >>> simulation.node_bulk_reset(
            ...     nodes=[
            ...         {'id': 'node-uuid-1'},
            ...         {'id': 'node-uuid-2'},
            ...     ],
            ... )

            >>> # Reset all nodes in simulation
            >>> nodes_to_reset = [{'id': n} for n in simulation.nodes.list()]
            >>> simulation.node_bulk_reset(nodes=nodes_to_reset)
        """
        ...

    def node_bulk_rebuild(
        self,
        *,
        nodes: List[NodeRebuildPayload],
        checkpoint: str | None = ...,
    ) -> None:
        """Rebuild specific nodes within this simulation.

        Rebuilding a node means returning the node to either the state of the current
        checkpoint of its simulation or its initial, first boot state.
        When rebuilding from the initial state, all repeatable instructions
        for selected nodes will be applied. All existing instructions
        created for the selected nodes which have not yet been completed
        will be failed. All existing instructions created for the selected nodes
        which have not yet been delivered will be cancelled.

        Args:
            nodes: List of node rebuild payloads, each containing a node object or ID
            checkpoint: Optional checkpoint ID to rebuild from

        Example:
            >>> # Rebuild a single node
            >>> simulation.node_bulk_rebuild(nodes=[{'id': node.id}])

            >>> # Rebuild multiple nodes using node IDs
            >>> simulation.node_bulk_rebuild(
            ...     nodes=[
            ...         {'id': 'node-uuid-1'},
            ...         {'id': 'node-uuid-2'},
            ...     ],
            ... )

            >>> # Rebuild all nodes in simulation
            >>> nodes_to_rebuild = [{'id': n} for n in simulation.nodes.list()]
            >>> simulation.node_bulk_rebuild(nodes=nodes_to_rebuild)
        """
        ...

class SimulationEndpointAPI(BaseEndpointAPI[Simulation]):
    """API client for simulation endpoints."""

    API_PATH: str
    model: type[Simulation]

    def create(
        self,
        *,
        name: str,
        sleep_at: datetime | None = ...,
        expires_at: datetime | None = ...,
        documentation: str | None = ...,
    ) -> Simulation:
        # fmt: off
        """Create a blank simulation.
        
        Args:
            name: Name for the new simulation
            sleep_at: When the simulation should be automatically put to sleep
            expires_at: When the simulation should be automatically deleted
            documentation: Documentation/description for the simulation
            
        Returns:
            The created Simulation instance
            
        Example:
            # Simple creation:
            >>> simulation = api.simulations.create(name='My Simulation')

            # With expiration and documentation:
            >>> from datetime import datetime, timedelta, timezone
            >>> expires = datetime.now(timezone.utc) + timedelta(days=7)
            >>> simulation = api.simulations.create(
            ...     name='My Simulation',
            ...     expires_at=expires,
            ...     documentation='Test simulation'
            ... )
        """
        # fmt: on
        ...

    def import_from_data(
        self,
        *,
        format: str,
        content: dict[str, Any] | str,
        name: str,
        ztp: str | None = ...,
        attempt_start: bool = ...,
        start_timeout: timedelta | None = ...,
    ) -> Simulation:
        # fmt: off
        """Import a simulation from raw data.
        
        Args:
            format: Format of the content ('JSON' or 'DOT')
            content: The topology content (dict for JSON, str for DOT)
            name: Name for the new simulation
            ztp: Optional ZTP script content
            attempt_start: When enabled, waits for the simulation creation to
                           complete and then starts it automatically
            start_timeout: Maximum time to wait for simulation creation
                           (default: 120 seconds)
            
        Returns:
            The imported Simulation instance
            
        Example:
            # Import from JSON:
            >>> simulation = api.simulations.import_from_data(
            ...     format='JSON', content={'nodes': [...]}, name='My Sim'
            ... )

            # Import and start:
            >>> simulation = api.simulations.import_from_data(
            ...     format='JSON',
            ...     content={'nodes': [...]},
            ...     name='My Sim',
            ...     attempt_start=True
            ... )

            # Import and start with custom timeout:
            >>> simulation = api.simulations.import_from_data(
            ...     format='JSON',
            ...     content={'nodes': [...]},
            ...     name='My Sim',
            ...     attempt_start=True,
            ...     start_timeout=300
            ... )
        """
        ...
        # fmt: on
    def import_from_simulation_manifest(
        self,
        *,
        simulation_manifest: dict[str, Any] | str | Path | TextIOBase,
        attempt_start: bool = ...,
        start_timeout: timedelta | None = ...,
    ) -> Simulation:
        # fmt: off
        """Import simulation from a full JSON manifest file.

        The manifest should contain all import parameters including:
        - format: 'JSON'
        - name: Simulation name
        - content: Topology data (for JSON format: dict with 'nodes', 'links',
          'oob', 'netq')
        - ztp: Optional ZTP script content

        Args:
            simulation_manifest: Full simulation manifest (dict, JSON string,
                                 file path, or file handle)
            attempt_start: When enabled, waits for the simulation creation to
                           complete and then starts it automatically
            start_timeout: Maximum time to wait for simulation creation
                           (default: 120 seconds)

        Returns:
            The created Simulation instance

        Raises:
            ValueError: If manifest is missing required fields
            FileNotFoundError: If file path doesn't exist
            JSONDecodeError: If JSON content is malformed

        Example:
            # From dict of simulation manifest:
            >>> simulation_manifest = {
            ...     'format': 'JSON',
            ...     'name': 'My Simulation',
            ...     'ztp': '#!/bin/bash\\necho "ZTP"',
            ...     'content': {
            ...         'nodes': {...},
            ...         'links': [],
            ...         'oob': True,
            ...         'netq': False
            ...     }
            ... }
            >>> simulation = api.simulations.import_from_simulation_manifest(
            ...     simulation_manifest=simulation_manifest
            ... )

            # With attempt_start:
            >>> simulation_manifest = {
            ...     'format': 'JSON',
            ...     'name': 'My Simulation',
            ...     'content': {...}
            ... }
            >>> simulation = api.simulations.import_from_simulation_manifest(
            ...     simulation_manifest=simulation_manifest,
            ...     attempt_start=True,
            ...     start_timeout=300
            ... )

            # From JSON file:
            >>> simulation = api.simulations.import_from_simulation_manifest(
            ...     '/path/to/manifest.json'
            ... )

            # From Path object:
            >>> from pathlib import Path
            >>> simulation = api.simulations.import_from_simulation_manifest(
            ...     Path('/path/to/manifest.json')
            ... )
        """
        ...
        # fmt: on
    def import_from_dot(
        self,
        *,
        topology_data: str | Path | TextIOBase,
        name: str,
        ztp: str | None = ...,
        attempt_start: bool = ...,
        start_timeout: timedelta | None = ...,
    ) -> Simulation:
        # fmt: off
        """Import simulation from DOT topology file/content.

        Args:
            topology_data: DOT topology content (string, file path, Path object,
                or file handle)
            name: Simulation name. If not provided, defaults to the graph name
                  declared in the DOT content
            ztp: Optional ZTP script content
            attempt_start: When enabled, waits for the simulation creation to
                           complete and then starts it automatically
            start_timeout: Maximum time to wait for simulation creation
                           (default: 120 seconds)

        Returns:
            The created Simulation instance

        Raises:
            ValueError: If content is invalid
            FileNotFoundError: If file path doesn't exist

        Example:
            # From DOT string:
            >>> dot_content = '''
            ... graph MyNetwork {
            ...     "server1" [ os="generic/ubuntu2204" ]
            ...     "switch1" [ os="cumulus/vx:5.11.0" ]
            ...     "server1":"eth1" -- "switch1":"swp1"
            ... }
            ... '''
            >>> simulation = api.simulations.import_from_dot(
            ...     topology_data=dot_content, name='My Simulation'
            ... )

            # Import and start:
            >>> simulation = api.simulations.import_from_dot(
            ...     topology_data=dot_content,
            ...     name='My Simulation',
            ...     attempt_start=True
            ... )

            # Import and start with custom timeout:
            >>> simulation = api.simulations.import_from_dot(
            ...     topology_data=dot_content,
            ...     name='My Simulation',
            ...     attempt_start=True,
            ...     start_timeout=300
            ... )

            # From DOT file path:
            >>> simulation = api.simulations.import_from_dot(
            ...     topology_data='/path/to/topology.dot', name='My Simulation'
            ... )

            # With ZTP script:
            >>> simulation = api.simulations.import_from_dot(
            ...     topology_data=dot_content,
            ...     name='My Simulation',
            ...     ztp='#!/bin/bash\\necho "ZTP"'
            ... )
        """
        ...
        # fmt: on
    def list(  # type: ignore[override]
        self,
        *,
        auto_netq_enabled: bool = ...,
        auto_oob_enabled: bool = ...,
        disable_auto_oob_dhcp: bool = ...,
        id: str = ...,
        limit: int = ...,
        name: str = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
        state: str = ...,
    ) -> Iterator[Simulation]:
        """List all simulations with optional filtering.

                Args:
                    auto_netq_enabled: Filter by auto NetQ enabled status
                    auto_oob_enabled: Filter by auto OOB enabled status
                    disable_auto_oob_dhcp: Filter by disable auto OOB DHCP status
                    id: Filter by simulation ID
                    limit: Number of results to return per page
                    name: Filter by simulation name
                    offset: The initial index from which to return the results
                    ordering: Order objects by field. Prefix with "-" for desc order
                    search: Search by name
                    state: Filter by simulation state (e.g., 'ACTIVE', 'INACTIVE',
                           'CREATING', 'CLONING', etc.)

        Returns:
            Iterator of Simulation instances

        Example:
                    >>> # List all simulations
            >>> for sim in api.simulations.list():
            ...     print(sim.name)
                    >>> # Filter by state
                    >>> for sim in api.simulations.list(state='ACTIVE'):
                    ...     print(sim.name)

                    >>> # Search by name
                    >>> for sim in api.simulations.list(search='my-sim'):
                    ...     print(sim.name)

                    >>> # Order by name descending
                    >>> for sim in api.simulations.list(ordering='-name'):
                    ...     print(sim.name)
        """
        ...

    def get(self, pk: PrimaryKey) -> Simulation:
        """Get a specific simulation by ID.

        Args:
            pk: The simulation ID (string or UUID)

        Returns:
            The Simulation instance

        Example:
            >>> simulation = api.simulations.get('sim-id')
        """
        ...

    def update(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        name: str | _MISSING_TYPE = ...,
        sleep_at: datetime | None | _MISSING_TYPE = ...,
        expires_at: datetime | None | _MISSING_TYPE = ...,
        documentation: str | None | _MISSING_TYPE = ...,
    ) -> Simulation:
        # fmt: off
        """Update a simulation's properties.

        Args:
            simulation: The simulation to update (Simulation object or ID)
            name: New name for the simulation
            sleep_at: When the simulation should be automatically put to sleep
            expires_at: When the simulation should be automatically deleted
            documentation: Documentation/description for the simulation

        Returns:
            The updated Simulation instance

        Example:
            # Using Simulation object:
            >>> updated_sim = api.simulations.update(
            ...     simulation=simulation, name='Updated Name'
            ... )

            # Using simulation ID:
            >>> updated_sim = api.simulations.update(
            ...     simulation='sim-123-abc',
            ...     name='Updated Name',
            ...     documentation='New docs'
            ... )
        """
        # fmt: on
        ...

    def export(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        image_ids: bool = ...,
        topology_format: Literal['JSON'] = 'JSON',
    ) -> dict[str, Any]:
        # fmt: off
        """Export a simulation.
        
        Args:
            simulation: The simulation to export (Simulation object or simulation ID)
            image_ids: Whether to include image IDs in the export
            topology_format: Format for the topology in the export
            
        Returns:
            Dictionary containing the exported simulation data
            
        Example:
            # Using Simulation object:
            >>> export_data = api.simulations.export(simulation=simulation)

            # Using simulation ID:
            >>> export_data = api.simulations.export(simulation='sim-123-abc')

            # With optional parameters:
            >>> export_data = api.simulations.export(
            ...     simulation=simulation, image_ids=True, topology_format='JSON'
            ... )
        """
        ...
        # fmt: on
    def clone(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        checkpoint: str | None = ...,
        attempt_start: bool = ...,
    ) -> Simulation:
        # fmt: off
        """Clone/duplicate a simulation.

        Args:
            simulation: The simulation to clone (Simulation object or simulation ID)
            checkpoint: Optional checkpoint ID to clone from. If not specified,
                       Air will find the most recent COMPLETE checkpoint if it exists.
            attempt_start: If the simulation should start immediately after cloning

        Returns:
            The cloned Simulation instance

        Example:
            # Using Simulation object:
            >>> cloned_sim = api.simulations.clone(simulation=sim)

            # Using simulation ID:
            >>> cloned_sim = api.simulations.clone(simulation='sim-123-abc')

            # Clone with checkpoint:
            >>> cloned_sim = api.simulations.clone(
            ...     simulation=sim, checkpoint='checkpoint-id'
            ... )

            # Clone and start immediately:
            >>> cloned_sim = api.simulations.clone(simulation=sim, attempt_start=True)
        """
        ...
    # fmt: on
    def enable_auto_oob(
        self, *, simulation: Simulation | PrimaryKey, disable_auto_oob_dhcp: bool = ...
    ) -> None:
        # fmt: off
        """Enable automatic Out-of-band management for a simulation.
        
        Args:
            simulation: The simulation object or simulation ID
            disable_auto_oob_dhcp: If True, disable DHCP on the OOB management network

            
        Example:
            # Enable OOB with DHCP (using simulation object):
            >>> api.simulations.enable_auto_oob(simulation=simulation)

            # Enable OOB using simulation ID:
            >>> api.simulations.enable_auto_oob(simulation='uuid-123')

            # Enable OOB without DHCP:
            >>> api.simulations.enable_auto_oob(
            ...     simulation=simulation, disable_auto_oob_dhcp=True
            ... )
        """
        # fmt: on
        ...

    def disable_auto_oob(self, *, simulation: Simulation | PrimaryKey) -> None:
        """Disable automatic Out-of-band management for a simulation.

        Args:
            simulation: The simulation object or simulation ID

        Example:
            # Using simulation object:
            >>> api.simulations.disable_auto_oob(simulation=simulation)

            # Using simulation ID:
            >>> api.simulations.disable_auto_oob(simulation='uuid-123')
        """
        ...

    def enable_auto_netq(self, *, simulation: Simulation | PrimaryKey) -> None:
        """Enable automatic NetQ for a simulation.

        Args:
            simulation: The simulation object or simulation ID

        Example:
            # Using simulation object:
            >>> api.simulations.enable_auto_netq(simulation=simulation)

            # Using simulation ID:
            >>> api.simulations.enable_auto_netq(simulation='uuid-123')
        """
        ...

    def disable_auto_netq(self, *, simulation: Simulation | PrimaryKey) -> None:
        """Disable automatic NetQ for a simulation.

        Args:
            simulation: The simulation object or simulation ID

        Example:
            # Using simulation object:
            >>> api.simulations.disable_auto_netq(simulation=simulation)

            # Using simulation ID:
            >>> api.simulations.disable_auto_netq(simulation='uuid-123')
        """
        ...

    def start(
        self, *, simulation: Simulation | PrimaryKey, checkpoint: str | None = ...
    ) -> None:
        """Start a simulation.

        Args:
            simulation: The simulation object or simulation ID to start
            checkpoint: Optional checkpoint ID to start from.
                       If not specified, the API will use its default behavior
                       (typically uses the most recent checkpoint if available).
                       If explicitly set to None, starts from clean state (rebuild).
                       If a string, starts from the specified checkpoint.

        Example:
            # Normal start (API determines behavior):
            >>> api.simulations.start(simulation=simulation)

            # Start using simulation ID:
            >>> api.simulations.start(simulation='uuid-123')

            # Start from specific checkpoint:
            >>> api.simulations.start(simulation=simulation, checkpoint='checkpoint-id')

            # Rebuild (start from clean state, no checkpoint):
            >>> api.simulations.start(simulation=simulation, checkpoint=None)
        """
        ...

    def rebuild(
        self, *, simulation: Simulation | PrimaryKey, checkpoint: str | None = ...
    ) -> None:
        """Rebuild a simulation from a given checkpoint.

        Tears down the simulation and starts it from the given checkpoint.
        If no checkpoint is provided, the simulation will be rebuilt from the clean state.

        Args:
            simulation: The simulation object or simulation ID to rebuild
            checkpoint: Optional checkpoint ID to rebuild from.
                        If not specified, the API will use its default behavior
                        (the current checkpoint the simulation is running off of).
                        If explicitly set to None, starts from clean state (rebuild).
                        If a string, starts from the specified checkpoint.

        Example:
            # Rebuild simulation from specific checkpoint:
            >>> api.simulations.rebuild(simulation=simulation, checkpoint='checkpoint-id')

            # Rebuild from clean state (no checkpoint):
            >>> api.simulations.rebuild(simulation=simulation, checkpoint=None)

            # Rebuild using simulation ID:
            >>> api.simulations.rebuild(simulation='uuid-123')
        """
        ...

    def shutdown(
        self, *, simulation: Simulation | PrimaryKey, create_checkpoint: bool = ...
    ) -> None:
        """Shut down a simulation.

        Args:
            simulation: The simulation object or simulation ID to shut down
            create_checkpoint: Whether to create a checkpoint before shutting down.
                              If not specified, the API will use its default behavior.

        Example:
            # Normal shutdown (API determines behavior):
            >>> api.simulations.shutdown(simulation=simulation)

            # Shutdown using simulation ID:
            >>> api.simulations.shutdown(simulation='uuid-123')

            # Explicitly create checkpoint before shutdown:
            >>> api.simulations.shutdown(simulation=simulation, create_checkpoint=True)

            # Explicitly don't create checkpoint:
            >>> api.simulations.shutdown(simulation=simulation, create_checkpoint=False)
        """
        ...

    def create_service(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        node_name: str,
        interface_name: str,
        node_port: int,
        name: str = ...,
        service_type: Literal['SSH', 'HTTPS', 'HTTP', 'OTHER'] = ...,
    ) -> Service:
        # fmt: off
        """Create service for a simulation by resolving node and interface names.

        Args:
            simulation: Simulation ID or object
            node_name: Node name in the simulation
            interface_name: Interface name on the node (e.g., 'eth0', 'swp1')
            node_port: Port number on the node
            name: Service name (optional)
            service_type: Service type - 'SSH', 'HTTPS', 'HTTP', or 'OTHER'

        Returns:
            Service object

        Raises:
            ValueError: If node or interface not found in simulation

        Example:
            >>> service = api.simulations.create_service(
            ...     simulation='sim-id',
            ...     node_name='server-1',
            ...     interface_name='eth0',
            ...     node_port=22,
            ...     service_type='SSH'
            ... )
        """
        ...
        # fmt: on
    def parse(
        self,
        *,
        topology_data: str,
        source_format: str,
        destination_format: str,
    ) -> dict[str, Any]:
        # fmt: off
        """Parse topology content between different formats.

        Convert topology data between different formats (e.g., DOT to JSON).

        Args:
            topology_data: The topology content to parse
            source_format: The format to parse the topology from (e.g., 'DOT').
            destination_format: The format to parse the topology to (e.g., 'JSON').

        Returns:
            Parsed topology data as a dictionary

        Example:
            >>> dot_content = '''
            ... graph MyNetwork {
            ...     "node-1" [ os="generic/ubuntu2204" cpu=2 ]
            ...     "node-2" [ os="generic/ubuntu2204" memory=2048 ]
            ...     "node-1":"eth1" -- "node-2":"eth1"
            ... }
            ... '''
            >>> # Convert DOT to JSON
            >>> parsed = api.simulations.parse(
            ...     topology_data=dot_content,
            ...     source_format='DOT',
            ...     destination_format='JSON',
            ... )
        """
        ...

    def node_bulk_assign(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        nodes: List[NodeAssignmentDataV3],
    ) -> None:
        """Bulk assign configurations to nodes in given simulation.

        Args:
            simulation: The simulation to bulk assign to
            nodes: List of node assignment data containing node,
                        user_data, and meta_data

        Example:
            >>> # Bulk assign cloud-init configs to multiple nodes
            >>> api.simulations.node_bulk_assign(
            ...     simulation=simulation,
            ...     nodes=[
            ...         {'node': 'node1', 'user_data': 'config1'},
            ...         {'node': 'node2', 'meta_data': 'config2'},
            ...     ],
            ... )
        """
        ...

    def node_bulk_reset(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        nodes: List[NodeResetPayload],
    ) -> None:
        """Reset specific nodes within a simulation.

        Resetting the node emulates the hardware reset button on physical machines
        where the machine is immediately restarted without a clean shutdown of the
        operating system. For nodes that are not currently running, this means simply
        booting them back up.

        Args:
            simulation: The simulation object or simulation ID containing the nodes
            nodes: List of node reset payloads, each containing a node object or ID

        Example:
            >>> # Reset a single node using node object
            >>> api.simulations.node_bulk_reset(
            ...     simulation=simulation,
            ...     nodes=[{'id': node}],
            ... )

            >>> # Reset multiple nodes using node IDs
            >>> api.simulations.node_bulk_reset(
            ...     simulation='sim-uuid-123',
            ...     nodes=[
            ...         {'id': 'node-uuid-1'},
            ...         {'id': 'node-uuid-2'},
            ...     ],
            ... )

            >>> # Reset nodes retrieved from simulation
            >>> nodes = [{'id': n} for n in simulation.nodes.list()]
            >>> api.simulations.node_bulk_reset(simulation=simulation, nodes=nodes)
        """
        ...

    def node_bulk_rebuild(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        nodes: List[NodeRebuildPayload],
        checkpoint: str | None = ...,
    ) -> None:
        """Rebuild specific nodes within a simulation.

        Rebuilding a node means returning the node to either the state of the current
        checkpoint of its simulation or its initial, first boot state.
        When rebuilding from the initial state, all repeatable instructions
        for selected nodes will be applied. All existing instruction
        created for the selected nodes which have not yet been completed
        will be failed. All existing instructions created for the selected nodes
        which have not yet been delivered will be cancelled.

        Args:
            simulation: The simulation object or simulation ID containing the nodes
            nodes: List of node rebuild payloads, each containing a node object or ID
            checkpoint: Optional checkpoint ID to rebuild from

        Example:
            >>> # Rebuild a single node using node object
            >>> api.simulations.node_bulk_rebuild(
            ...     simulation=simulation,
            ...     nodes=[{'id': node}],
            ... )

            >>> # Rebuild multiple nodes using node IDs
            >>> api.simulations.node_bulk_rebuild(
            ...     simulation='sim-uuid-123',
            ...     nodes=[
            ...         {'id': 'node-uuid-1'},
            ...         {'id': 'node-uuid-2'},
            ...     ],
            ... )
        """
        ...
