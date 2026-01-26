# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import cached_property, singledispatchmethod
from http import HTTPStatus
from io import TextIOBase
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator, Literal

from air_sdk.air_model import (
    AirModel,
    BaseEndpointAPI,
    PrimaryKey,
)
from air_sdk.bc import (
    BaseCompatMixin,
    SimulationCompatMixin,
    SimulationEndpointAPICompatMixin,
)
from air_sdk.const import TopologyFormat
from air_sdk.endpoints import mixins
from air_sdk.endpoints.history import History
from air_sdk.exceptions import AirUnexpectedResponse
from air_sdk.utils import (
    join_urls,
    raise_if_invalid_response,
    validate_payload_types,
)
from air_sdk.utils import wait_for_state as wait_for_state_util

if TYPE_CHECKING:
    from air_sdk.endpoints.interfaces import InterfaceEndpointAPI
    from air_sdk.endpoints.node_instructions import NodeInstructionEndpointAPI
    from air_sdk.endpoints.nodes import NodeEndpointAPI
    from air_sdk.endpoints.services import Service, ServiceEndpointAPI
    from air_sdk.endpoints.ztp_scripts import ZTPScript


@dataclass(eq=False)
class Simulation(BaseCompatMixin, SimulationCompatMixin, AirModel):
    id: str = field(repr=False)
    name: str
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    state: str
    creator: str
    auto_oob_enabled: bool | None = field(repr=False)
    disable_auto_oob_dhcp: bool | None = field(repr=False)
    auto_netq_enabled: bool | None = field(repr=False)
    netq_username: str | None = field(default=None, repr=False)
    netq_password: str | None = field(default=None, repr=False)
    sleep_at: datetime | None = field(default=None, repr=False)
    expires_at: datetime | None = field(default=None, repr=False)
    documentation: str | None = field(default=None, repr=False)
    complete_checkpoint_count: int = field(default=0, repr=False)

    @classmethod
    def get_model_api(cls) -> type[SimulationEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return SimulationEndpointAPI

    @property
    def model_api(self) -> SimulationEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    def update(self, **kwargs: Any) -> None:
        self.model_api.update(simulation=self, **kwargs)

    def enable_auto_oob(self, **kwargs: Any) -> None:
        self.model_api.enable_auto_oob(simulation=self, **kwargs)

    def disable_auto_oob(self, **kwargs: Any) -> None:
        self.model_api.disable_auto_oob(simulation=self, **kwargs)

    def enable_auto_netq(self, **kwargs: Any) -> None:
        self.model_api.enable_auto_netq(simulation=self, **kwargs)

    def disable_auto_netq(self, **kwargs: Any) -> None:
        self.model_api.disable_auto_netq(simulation=self, **kwargs)

    @validate_payload_types
    def create_ztp_script(self, *, content: str, **kwargs: Any) -> ZTPScript:
        ztp_script_endpoint_api = self.__api__.ztp_scripts
        url = ztp_script_endpoint_api.url.format(simulation_id=self.id)
        data = mixins.serialize_payload({'content': content, **kwargs})
        response = self.__api__.client.post(url, data=data)
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        self.refresh()
        self.ztp_script = ztp_script_endpoint_api.load_model(
            response.json() | {'simulation': self}
        )
        return self.ztp_script

    @validate_payload_types
    def update_ztp_script(self, *, content: str, **kwargs: Any) -> ZTPScript:
        ztp_script_endpoint_api = self.__api__.ztp_scripts
        updated_script = ztp_script_endpoint_api.patch(
            simulation=self, content=content, **kwargs
        )
        self.ztp_script = updated_script
        return updated_script

    def delete_ztp_script(self) -> None:
        ztp_script_endpoint_api = self.__api__.ztp_scripts
        ztp_script_endpoint_api.delete(simulation=self)
        self.clear_cached_property('ztp_script')

    def export(self, **kwargs: Any) -> dict[str, Any]:
        return self.model_api.export(simulation=self, **kwargs)

    def clone(self, **kwargs: Any) -> Simulation:
        return self.model_api.clone(simulation=self, **kwargs)

    def start(self, **kwargs: Any) -> None:
        self.model_api.start(simulation=self, **kwargs)

    def shutdown(self, **kwargs: Any) -> None:
        self.model_api.shutdown(simulation=self, **kwargs)

    def rebuild(self, **kwargs: Any) -> None:
        self.model_api.rebuild(simulation=self, **kwargs)

    def wait_for_state(
        self,
        target_states: str | list[str],
        timeout: timedelta | None = None,
        poll_interval: timedelta | None = None,
        error_states: str | list[str] | None = None,
    ) -> None:
        wait_for_state_util(
            self,
            target_states,
            state_field='state',
            timeout=timeout,
            poll_interval=poll_interval,
            error_states=error_states,
        )

    def set_sleep_time(self, sleep_at: datetime | None) -> None:
        self.update(sleep_at=sleep_at)

    def set_expire_time(self, expires_at: datetime | None) -> None:
        self.update(expires_at=expires_at)

    # RELATED MODELS
    @cached_property
    def ztp_script(self) -> ZTPScript | None:
        try:
            return self.__api__.ztp_scripts.get(simulation=self)
        except AirUnexpectedResponse as e:
            # Only return None for 404 (ZTP script not found)
            if e.status_code == HTTPStatus.NOT_FOUND:
                return None
            # Re-raise other errors (500, 403, None, etc.) as they indicate real problems
            raise

    def get_history(self, **kwargs: Any) -> Iterator[History]:
        return self.__api__.histories.list(
            model='simulation', object_id=self.id, **kwargs
        )

    @property
    def nodes(self) -> NodeEndpointAPI:
        from air_sdk.endpoints.nodes import NodeEndpointAPI

        return NodeEndpointAPI(
            self.__api__, default_filters={'simulation': str(self.__pk__)}
        )

    @property
    def interfaces(self) -> InterfaceEndpointAPI:
        from air_sdk.endpoints.interfaces import InterfaceEndpointAPI

        return InterfaceEndpointAPI(
            self.__api__, default_filters={'simulation': str(self.__pk__)}
        )

    @property
    def node_instructions(self) -> NodeInstructionEndpointAPI:
        from air_sdk.endpoints.node_instructions import NodeInstructionEndpointAPI

        return NodeInstructionEndpointAPI(
            self.__api__, default_filters={'simulation': str(self.__pk__)}
        )

    @property
    def services(self) -> ServiceEndpointAPI:
        from air_sdk.endpoints.services import ServiceEndpointAPI

        return ServiceEndpointAPI(
            self.__api__, default_filters={'simulation': str(self.__pk__)}
        )

    def create_service(self, **kwargs: Any) -> Service:
        return self.model_api.create_service(simulation=self, **kwargs)

    def node_bulk_assign(self, **kwargs: Any) -> None:
        return self.model_api.node_bulk_assign(simulation=self, **kwargs)

    def node_bulk_reset(self, **kwargs: Any) -> None:
        self.model_api.node_bulk_reset(simulation=self, **kwargs)

    def node_bulk_rebuild(self, **kwargs: Any) -> None:
        self.model_api.node_bulk_rebuild(simulation=self, **kwargs)


class SimulationEndpointAPI(
    SimulationEndpointAPICompatMixin,
    mixins.ListApiMixin[Simulation],
    mixins.CreateApiMixin[Simulation],
    mixins.GetApiMixin[Simulation],
    mixins.PatchApiMixin[Simulation],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Simulation],
):
    API_PATH = 'simulations'
    IMPORT_PATH = 'import'
    EXPORT_PATH = 'export'
    START_PATH = 'start'
    SHUTDOWN_PATH = 'shutdown'
    PARSE_PATH = 'parse'
    REBUILD_PATH = 'rebuild'
    NODE_BULK_ASSIGN_PATH = 'nodes/bulk-assign'
    NODE_BULK_RESET_PATH = 'nodes/bulk-reset'
    NODE_BULK_REBUILD_PATH = 'nodes/bulk-rebuild'
    model = Simulation

    @singledispatchmethod
    def _resolve_json_from_source(
        self, source: dict[str, Any] | str | Path | TextIOBase
    ) -> dict[str, Any]:
        """Resolve JSON data from various sources.

        Handles source as dict, JSON string, file path, or file object.

        Args:
            source: JSON data as dict, JSON string, Path to JSON file, or file object
        Returns:
            Resolved dict
        Raises:
            ValueError: If resolved content is not a dict
            JSONDecodeError: If string/file content is not valid JSON
            FileNotFoundError: If file path does not exist
        """
        # Default implementation: handle dict
        if not isinstance(source, dict):
            raise ValueError(f'JSON data must be a dict, got {type(source)}')
        return source

    @_resolve_json_from_source.register
    def _(self, source: TextIOBase) -> dict[str, Any]:
        """Resolve JSON from file object."""
        resolved = json.load(source)
        if not isinstance(resolved, dict):
            raise ValueError(f'JSON data must be a dict, got {type(resolved)}')
        return resolved

    @_resolve_json_from_source.register
    def _(self, source: Path) -> dict[str, Any]:
        """Resolve JSON from Path object."""
        with source.open('r') as f:
            resolved = json.load(f)
        if not isinstance(resolved, dict):
            raise ValueError(f'JSON data must be a dict, got {type(resolved)}')
        return resolved

    @_resolve_json_from_source.register
    def _(self, source: str) -> dict[str, Any]:
        """Resolve JSON from string (file path or JSON string)."""
        # Try as file path first
        path = Path(source)
        if path.exists() and path.is_file():
            with path.open('r') as f:
                resolved = json.load(f)
        else:
            # Parse as JSON string
            # TODO: Consider raising FileNotFoundError for path-like strings
            #  that don't exist (e.g., contain '/', '\', or end with '.json')
            #  to provide clearer error messages instead of JSONDecodeError
            resolved = json.loads(source)

        if not isinstance(resolved, dict):
            raise ValueError(f'JSON data must be a dict, got {type(resolved)}')
        return resolved

    def _resolve_simulation_manifest(
        self, simulation_manifest: dict[str, Any] | str | Path | TextIOBase
    ) -> dict[str, Any]:
        # First, resolve the top-level manifest
        resolved = self._resolve_json_from_source(simulation_manifest)

        # Second, resolve the content field if it needs resolution (for JSON format)
        if 'content' in resolved and 'format' in resolved:
            format_type = resolved['format']
            if (
                isinstance(format_type, str)
                and format_type.upper() == TopologyFormat.JSON
            ):
                content = resolved['content']
                # Only resolve if content is not already a dict
                if not isinstance(content, dict):
                    resolved['content'] = self._resolve_json_from_source(content)

        return resolved

    def _resolve_dot_topology(self, topology: str | Path | TextIOBase) -> str:
        if isinstance(topology, TextIOBase):
            resolved = topology.read()
        elif isinstance(topology, Path):
            with topology.open('r') as f:
                resolved = f.read()
        elif isinstance(topology, str):
            # Try as file path first
            path = Path(topology)
            if path.exists() and path.is_file():
                with path.open('r') as f:
                    resolved = f.read()
            else:
                # Use as raw DOT content
                resolved = topology

        if not isinstance(resolved, str):
            raise ValueError(
                f'DOT topology format requires str content, got {type(resolved)}'
            )

        return resolved

    def _wait_and_start_simulation(
        self,
        simulation: Simulation,
        timeout: timedelta = timedelta(seconds=120),
        poll_interval: timedelta = timedelta(seconds=2),
    ) -> None:
        """Wait for simulation to be ready and then start it.

        Args:
            simulation: The simulation to wait for and start
            timeout: Maximum time to wait (default: 120 seconds)
            poll_interval: Time between status checks (default: 2 seconds)

        Raises:
            ValueError: If simulation enters an error state
            TimeoutError: If timeout is exceeded before simulation is ready
        """
        # TODO: Use constants when Sim state MR is merged
        # Wait for simulation to be INACTIVE (ready to start)
        simulation.wait_for_state(
            target_states='INACTIVE',
            timeout=timeout,
            poll_interval=poll_interval,
            error_states='INVALID',
        )

        # Start the simulation
        simulation.start()

    @validate_payload_types
    def import_from_data(
        self,
        *,
        attempt_start: bool = False,
        start_timeout: timedelta | None = None,
        **kwargs: Any,
    ) -> Simulation:
        # Let API validate format/content and all parameters
        response = self.__api__.client.post(
            join_urls(self.url, self.IMPORT_PATH),
            data=mixins.serialize_payload(kwargs),
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        sim: Simulation = self.load_model(response.json())

        # If attempt_start, wait for simulation to be ready and start it
        if attempt_start:
            if start_timeout is not None:
                self._wait_and_start_simulation(sim, timeout=start_timeout)
            else:
                self._wait_and_start_simulation(sim)

        return sim

    @validate_payload_types
    def import_from_simulation_manifest(
        self,
        *,
        simulation_manifest: dict[str, Any] | str | Path | TextIOBase,
        attempt_start: bool = False,
        start_timeout: timedelta | None = None,
    ) -> Simulation:
        # Resolve manifest (including content field)
        resolved_manifest = self._resolve_simulation_manifest(simulation_manifest)

        # Pass attempt_start and start_timeout as separate parameters
        # (they should not be in the manifest itself)
        return self.import_from_data(
            **resolved_manifest,
            attempt_start=attempt_start,
            start_timeout=start_timeout,
        )

    @validate_payload_types
    def import_from_dot(
        self,
        *,
        topology_data: str | Path | TextIOBase,
        attempt_start: bool = False,
        start_timeout: timedelta | None = None,
        **kwargs: Any,
    ) -> Simulation:
        # Resolve DOT topology data
        resolved_content = self._resolve_dot_topology(topology_data)

        # Require name to be provided
        # Note: BC layer already maps 'title' to 'name', so we only check for 'name' here
        # TODO: Remove this once the API allows create without name and let the DOT2JSON
        #  parser to extract the name from the DOT content
        if 'name' not in kwargs:
            raise ValueError(
                'The "name" (or "title") parameter is required when importing '
                'DOT topology. Please provide a name for the simulation.'
            )

        # Call import_from_data with DOT format
        return self.import_from_data(
            format=TopologyFormat.DOT,
            content=resolved_content,
            attempt_start=attempt_start,
            start_timeout=start_timeout,
            **kwargs,
        )

    @validate_payload_types
    def update(self, *, simulation: Simulation | PrimaryKey, **kwargs: Any) -> Simulation:
        sim_id = simulation.id if isinstance(simulation, Simulation) else simulation
        result = self.patch(sim_id, **kwargs)
        if isinstance(simulation, Simulation):
            # Refresh the original object using the patch response data
            simulation.__refresh__(refreshed_obj=result)
        return result

    @validate_payload_types
    def export(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        topology_format: Literal['JSON'] = 'JSON',
        **kwargs: Any,
    ) -> dict[str, Any]:
        sim_id = simulation.id if isinstance(simulation, Simulation) else simulation
        url = join_urls(self.url, str(sim_id), self.EXPORT_PATH)
        response = self.__api__.client.get(
            url,
            params=json.loads(
                mixins.serialize_payload({'topology_format': topology_format, **kwargs})
            ),
        )
        raise_if_invalid_response(response)
        response_data: dict[str, Any] = response.json()
        return response_data

    @validate_payload_types
    def clone(self, *, simulation: Simulation | PrimaryKey, **kwargs: Any) -> Simulation:
        url = join_urls(self.url, 'clone')
        response = self.__api__.client.post(
            url, data=mixins.serialize_payload({'simulation': simulation, **kwargs})
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        return self.load_model(response.json())

    @validate_payload_types
    def enable_auto_oob(
        self, *, simulation: Simulation | PrimaryKey, **kwargs: Any
    ) -> None:
        url = mixins.build_resource_url(self.url, simulation, 'enable-auto-oob')
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(response, data_type=None)
        if isinstance(simulation, Simulation):
            simulation.refresh()

    @validate_payload_types
    def disable_auto_oob(
        self, *, simulation: Simulation | PrimaryKey, **kwargs: Any
    ) -> None:
        url = mixins.build_resource_url(self.url, simulation, 'disable-auto-oob')
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(response, data_type=None)
        if isinstance(simulation, Simulation):
            simulation.refresh()

    @validate_payload_types
    def enable_auto_netq(
        self, *, simulation: Simulation | PrimaryKey, **kwargs: Any
    ) -> None:
        url = mixins.build_resource_url(self.url, simulation, 'enable-auto-netq')
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(response, data_type=None)
        if isinstance(simulation, Simulation):
            simulation.refresh()

    @validate_payload_types
    def disable_auto_netq(
        self, *, simulation: Simulation | PrimaryKey, **kwargs: Any
    ) -> None:
        url = mixins.build_resource_url(self.url, simulation, 'disable-auto-netq')
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(response, data_type=None)
        if isinstance(simulation, Simulation):
            simulation.refresh()

    @validate_payload_types
    def start(self, *, simulation: Simulation | PrimaryKey, **kwargs: Any) -> None:
        url = mixins.build_resource_url(self.url, simulation, self.START_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        if isinstance(simulation, Simulation):
            simulation.refresh()
        raise_if_invalid_response(response)

    @validate_payload_types
    def rebuild(self, *, simulation: Simulation | PrimaryKey, **kwargs: Any) -> None:
        url = mixins.build_resource_url(self.url, simulation, self.REBUILD_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        if isinstance(simulation, Simulation):
            simulation.refresh()
        raise_if_invalid_response(response)

    @validate_payload_types
    def shutdown(self, *, simulation: Simulation | PrimaryKey, **kwargs: Any) -> None:
        url = mixins.build_resource_url(self.url, simulation, self.SHUTDOWN_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        if isinstance(simulation, Simulation):
            simulation.refresh()
        raise_if_invalid_response(response)

    @validate_payload_types
    def create_service(
        self,
        *,
        simulation: Simulation | PrimaryKey,
        **kwargs: Any,
    ) -> Service:
        # Get simulation object if needed
        sim = simulation if isinstance(simulation, Simulation) else self.get(simulation)

        # BC: If 'interface' param provided, delegate to services API
        # (which handles 'node:interface' parsing via ServiceEndpointAPICompatMixin)
        if 'interface' in kwargs:
            # Pass simulation for BC 'node:interface' string resolution
            return sim.services.create(simulation=sim, **kwargs)  # type: ignore[call-arg]

        # V3: Extract required parameters
        node_name = kwargs.pop('node_name', None)
        interface_name = kwargs.pop('interface_name', None)

        if not node_name or not interface_name:
            raise ValueError(
                "Must provide either 'interface' parameter or both "
                "'node_name' and 'interface_name' parameters"
            )

        # Resolve node name to Node object
        node_obj = next(sim.nodes.list(name=node_name), None)
        if not node_obj:
            raise ValueError(f'Node "{node_name}" not found in simulation')

        # Resolve interface name to interface ID
        interface_obj = next(
            self.__api__.interfaces.list(node=node_obj.id, name=interface_name),
            None,
        )
        if not interface_obj:
            raise ValueError(f'Interface "{interface_name}" not found on node')
        interface_id = str(interface_obj.id)

        return sim.services.create(interface=interface_id, **kwargs)

    def parse(self, **kwargs: Any) -> dict[str, Any]:
        url = join_urls(self.url, self.PARSE_PATH)
        response = self.__api__.client.post(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(response)
        response_data: dict[str, Any] = response.json()
        return response_data

    def node_bulk_assign(self, **kwargs: Any) -> None:
        url = join_urls(self.url, self.NODE_BULK_ASSIGN_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(
            response, status_code=HTTPStatus.NO_CONTENT, data_type=None
        )

    def node_bulk_reset(self, **kwargs: Any) -> None:
        url = join_urls(self.url, self.NODE_BULK_RESET_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(
            response, status_code=HTTPStatus.NO_CONTENT, data_type=None
        )

    def node_bulk_rebuild(self, **kwargs: Any) -> None:
        url = join_urls(self.url, self.NODE_BULK_REBUILD_PATH)
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(kwargs))
        raise_if_invalid_response(
            response, status_code=HTTPStatus.NO_CONTENT, data_type=None
        )
