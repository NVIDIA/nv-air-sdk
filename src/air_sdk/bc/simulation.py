# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Simulation-specific backward compatibility for v1/v2 SDK.
"""

from __future__ import annotations

import warnings
from datetime import timedelta
from typing import TYPE_CHECKING, Any, cast

from air_sdk.air_model import PrimaryKey
from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.bc.decorators import deprecated
from air_sdk.bc.utils import (
    drop_removed_fields,
    handle_boolean_datetime_fields,
    map_field_names,
)
from air_sdk.types import SimState

if TYPE_CHECKING:
    from air_sdk.endpoints.simulations import Simulation


class SimulationState(str):
    """A string subclass that provides BC for simulation state comparisons.

    This allows old state names (v1/v2) to match new state names (v3).

    Example:
        >>> sim.state  # Returns 'ACTIVE'
        >>> sim.state == 'ACTIVE'  # True
        >>> sim.state == 'LOADED'  # True (BC mapping)
    """

    # Mapping: old state name → list of new state names
    _OLD_TO_NEW: dict[str, list[str]] = {
        'LOADING': [
            SimState.BOOTING,
            SimState.PREPARE_BOOT,
            SimState.REQUESTING,
            SimState.PROVISIONING,
        ],
        'LOADED': [
            SimState.ACTIVE,
            SimState.PREPARE_REBUILD,
            SimState.REBUILDING,
        ],
        'NEW': [SimState.INACTIVE],
        'STORED': [SimState.INACTIVE],
        'STORING': [
            SimState.SHUTTING_DOWN,
            SimState.PREPARE_SHUTDOWN,
            SimState.SAVING,
            SimState.PREPARE_PURGE,
            SimState.PURGING,
        ],
        'SNAPSHOT': [SimState.DEMO],
    }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, str):
            return False

        # Direct match
        if str.__eq__(self, other):
            return True

        # Check if `other` is an old alias that maps to our current value
        # e.g., self='ACTIVE', other='LOADED' → True
        if other in self._OLD_TO_NEW:
            # Warn about deprecated state name usage
            mapped_states = ', '.join(self._OLD_TO_NEW[other])
            warnings.warn(
                f"Simulation state '{other}' is deprecated and is being mapped to "
                f'new state(s): {mapped_states}. '
                f'Please update your code to use the new state names.',
                DeprecationWarning,
                stacklevel=2,
            )
            return str(self) in self._OLD_TO_NEW[other]

        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        # When __eq__ is overridden, Python sets __hash__ = None by default,
        # making the object unhashable. We restore str's hash behavior so
        # SimulationState can still be used in sets and as dict keys.
        return str.__hash__(self)


def _extract_oob_netq_fields(
    kwargs: dict[str, Any],
) -> tuple[bool | None, bool | None, bool | None]:
    """Extract OOB/NetQ fields from kwargs for routing to dedicated endpoints.

    Extracts and removes auto_oob_enabled, disable_auto_oob_dhcp, and
    auto_netq_enabled from kwargs (modified in-place).

    Args:
        kwargs: Dictionary to extract OOB/NetQ fields from (modified in-place)

    Returns:
        Tuple of (auto_oob_enabled, disable_auto_oob_dhcp, auto_netq_enabled)
        Each value is None if not present in kwargs.
    """
    auto_oob_enabled = kwargs.pop('auto_oob_enabled', None)
    # disable_auto_oob_dhcp only applies when enabling OOB
    disable_auto_oob_dhcp = kwargs.pop('disable_auto_oob_dhcp', None)
    auto_netq_enabled = kwargs.pop('auto_netq_enabled', None)

    return auto_oob_enabled, disable_auto_oob_dhcp, auto_netq_enabled


class SimulationCompatMixin(AirModelCompatMixin):
    """Mixin providing Simulation-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with simulation fields and methods from older
    SDK versions:
    - Field mappings: title → name, owner → creator (v1/v2 → v3)
    - Method mappings: Various control methods
    """

    # Field mappings: old (v1/v2) → new (v3)
    _FIELD_MAPPINGS = {
        'title': 'name',
        'owner': 'creator',
        'oob_auto_enabled': 'auto_oob_enabled',
        'netq_auto_enabled': 'auto_netq_enabled',
        'start': 'attempt_start',
    }

    # Boolean datetime field mappings: bool field → datetime field (v1/v2 → v3)
    _BOOLEAN_DATETIME_FIELDS = {
        'expires': 'expires_at',
        'sleep': 'sleep_at',
    }

    # Fields and filters that were removed in v3
    _REMOVED_FIELDS = ['metadata', 'organization', 'preferred_worker', 'write_ok']

    def __post_init__(self, _api: Any) -> None:
        """Convert state field to SimulationState for BC comparisons."""
        # Call parent __post_init__ first
        super().__post_init__(_api)  # type: ignore[misc]

        # Wrap state in SimulationState if it's a plain string
        state = getattr(self, 'state', None)
        if state is not None and not isinstance(state, SimulationState):
            object.__setattr__(self, 'state', SimulationState(state))

    def __getattr__(self, name: str) -> Any:
        """Handle simulation-specific computed fields and delegate mapping to base.

        Provides computed v1/v2 boolean fields:
        - sleep: computed from sleep_at (True if sleep_at is set)
        - expires: computed from expires_at (True if expires_at is set)

        Field mappings and removed fields are handled by AirModelCompatMixin.
        """
        # Computed boolean fields for v1/v2 compatibility
        if name == 'sleep':
            return super().__getattribute__('sleep_at') is not None
        if name == 'expires':
            return super().__getattribute__('expires_at') is not None

        # Let base mixin handle field mappings and removed fields
        # This will eventually call the parent's __getattribute__
        return super().__getattr__(name)

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update method with field name compatibility for Simulations.

        Normalizes old (v1/v2) field names to v3 equivalents
        (see _FIELD_MAPPINGS).

        Drops unsupported fields:
        - expires, sleep (boolean) → use expires_at, sleep_at (datetime)
        - Fields in _REMOVED_FIELDS

        Routes OOB/NetQ fields to dedicated endpoints:
        - auto_oob_enabled, disable_auto_oob_dhcp → enable/disable_auto_oob()
        - auto_netq_enabled → enable/disable_auto_netq()

        Note:
            This method overrides the parent update() to provide field mapping.
        """
        # Clean up kwargs for v3 compatibility
        handle_boolean_datetime_fields(kwargs, self._BOOLEAN_DATETIME_FIELDS)
        drop_removed_fields(kwargs, self._REMOVED_FIELDS)
        map_field_names(kwargs, self._FIELD_MAPPINGS)

        # Extract and route OOB/NetQ fields to dedicated endpoints
        # Note: NetQ depends on OOB, so we handle in this order:
        # 1. Disable NetQ (if needed)
        # 2. Enable/disable OOB
        # 3. Enable NetQ (if needed)
        auto_oob_enabled, disable_auto_oob_dhcp, auto_netq_enabled = (
            _extract_oob_netq_fields(kwargs)
        )

        # Step 1: Disable NetQ first (if disabling) since NetQ requires OOB
        if auto_netq_enabled is False:
            self.disable_auto_netq()

        # Step 2: Handle OOB enable/disable
        if auto_oob_enabled is not None:
            if auto_oob_enabled:
                enable_kwargs = {}
                if disable_auto_oob_dhcp is not None:
                    enable_kwargs['disable_auto_oob_dhcp'] = disable_auto_oob_dhcp
                self.enable_auto_oob(**enable_kwargs)
            else:
                self.disable_auto_oob()

        # Step 3: Enable NetQ last (if enabling) since it requires OOB to be enabled
        if auto_netq_enabled is True:
            self.enable_auto_netq()

        # Call the parent update() method for remaining fields
        if kwargs:  # Only call if there are remaining fields
            super().update(*args, **kwargs)  # type: ignore[misc]

    @deprecated('The control() method is deprecated and may be removed in the future.')
    def control(self, action: str, **kwargs: Any) -> dict[str, Any] | Any:
        """Legacy control method from v1/v2.

        Sends a control command to the simulation.

        Args:
            action: Control command ('load', 'store', 'destroy', 'duplicate',
                    'rebuild', 'extend')
            **kwargs: Additional parameters for the control action

        Returns:
            Response dictionary from the API

        Note:
            This method is deprecated. Use explicit methods instead:
            - control(action='load') -> start()
            - control(action='store') -> shutdown()
            - control(action='destroy') -> delete()
            - control(action='duplicate') -> duplicate()
            - control(action='rebuild') -> start(checkpoint=None)
            - control(action='extend') -> extend()

        Example:
            >>> # v1/v2 style (still supported)
            >>> simulation.control(action='load')
            {'result': 'success', 'message': 'Simulation starting!'}

            >>> # v3 style (recommended)
            >>> simulation.start()
        """
        if action == 'load':
            self.start()
            return {'result': 'success', 'message': 'Simulation starting!'}
        elif action == 'store':
            self.shutdown()
            return {'result': 'success', 'message': 'Simulation being stored!'}
        elif action == 'destroy':
            self.delete()
            return {'result': 'success', 'message': 'Simulation stopping!'}
        elif action == 'duplicate':
            # duplicate() returns a Simulation object
            new_sim = self.duplicate(**kwargs)
            # Return dict format matching v1 control() behavior
            # Check for both 'start' (v1/v2) and 'attempt_start' (v3) since
            # this is a deprecated legacy method
            return {
                'result': 'success',
                'message': (
                    'Duplicated simulation starting!'
                    if kwargs.get('attempt_start') or kwargs.get('start')
                    else 'Duplicated simulation'
                ),
                'simulation': new_sim,
            }
        elif action == 'rebuild':
            # Call v3 rebuild method directly
            self.__api__.simulations.rebuild(simulation=self)
            return {'result': 'success', 'message': 'Simulation starting!'}
        elif action == 'extend':
            return self.extend(**kwargs)
        else:
            raise ValueError(
                f"Unknown action '{action}'. "
                f'Use explicit methods: start(), shutdown(), delete(), '
                f'duplicate(), rebuild(), extend()'
            )

    @deprecated(
        'load() is deprecated and may be removed in the future. Use start() instead.'
    )
    def load(self) -> None:
        """Legacy load method from v1/v2. Alias for start().

        Note:
            This method is deprecated. Use start() instead.
            Maintained for backward compatibility with v1/v2 SDK.

        Example:
            >>> # v1/v2 style (still supported)
            >>> simulation.load()

            >>> # v3 style (recommended)
            >>> simulation.start()
        """
        self.start()

    @deprecated(
        'store() is deprecated and may be removed in the future. Use shutdown() instead.'
    )
    def store(self) -> None:
        """Legacy store method from v1/v2. Store and power off the simulation.

        Note:
            This method is deprecated. Use shutdown() instead.
            Maintained for backward compatibility with v1/v2 SDK.

        Example:
            >>> # v1/v2 style (still supported)
            >>> simulation.store()

            >>> # v3 style (recommended)
            >>> simulation.shutdown()
        """
        self.shutdown()

    @deprecated(
        'stop() is deprecated and may be removed in the future. Use shutdown() instead.'
    )
    def stop(self) -> None:
        """Legacy stop method from v1/v2. Alias for shutdown().

        Note:
            This method is deprecated. Use shutdown() instead.
            Maintained for backward compatibility with v1/v2 SDK.

        Example:
            >>> # v1/v2 style (still supported)
            >>> simulation.stop()

            >>> # v3 style (recommended)
            >>> simulation.shutdown()
        """
        self.shutdown()

    # simulation.create_service() BC handling is now in Simulation.create_service()
    # No override needed - the main method delegates to services.create()
    # for BC 'interface' parameter

    # fmt: on
    def preferences(self, **kwargs: Any) -> Any:
        """
        User preferences endpoint is not supported in the current air-api version.
        """
        raise NotImplementedError(
            'User preferences endpoint is not supported in the current air-api version.'
        )

    def duplicate(self, **kwargs: Any) -> Any:
        """Legacy duplicate method from v1/v2.

        Duplicates/clones the simulation. This is the v1/v2 backward compatibility
        wrapper that calls the v3 clone() method.

        Args:
            **kwargs: Additional parameters for duplication
                      (e.g., checkpoint, start)

        Returns:
            New Simulation object (the duplicate)

        Note:
            This method is deprecated (warning shown by API method).
            In v3, use clone() instead.
            Field mapping: v1/v2 'start' → v3 'attempt_start'

        Example:
            >>> # v1/v2 style (still supported)
            >>> new_sim = simulation.duplicate()
            >>> print(new_sim.name)

            >>> # v1/v2 style with start parameter
            >>> new_sim = simulation.duplicate(start=True)

            >>> # v3 style (recommended)
            >>> new_sim = simulation.clone()
            >>> new_sim = simulation.clone(attempt_start=True)

            >>> # Or via control (v1)
            >>> result = simulation.control(action='duplicate')
        """
        # Delegate to API-level duplicate() which handles parameter mapping
        return self.model_api.duplicate(simulation=self, **kwargs)

    @deprecated(
        'extend() is deprecated and may be removed in the future. '
        'Use set_sleep_time() instead.'
    )
    def extend(self, **kwargs: Any) -> dict[str, Any]:
        """Legacy extend method from v1/v2.

        Extends the simulation sleep time by 12 hours (default behavior from legacy API).
        Adds 12 hours to the current sleep_at time.

        Args:
            **kwargs: Additional parameters (currently unused, kept for compatibility)

        Returns:
            Response dictionary with result and new sleep_at time

        Note:
            In v3, this wraps set_sleep_time() to maintain backward compatibility.
            The legacy API added 12 hours to the existing sleep_at time.
            The API will enforce any constraints (e.g., expiration limits).

        Example:
            >>> # v1/v2 style (still supported)
            >>> result = simulation.extend()
            >>> print(result['message'])  # New sleep_at time

            >>> # v3 style (recommended)
            >>> from datetime import datetime, timedelta, timezone
            >>> new_sleep = datetime.now(timezone.utc) + timedelta(hours=12)
            >>> simulation.set_sleep_time(new_sleep)
        """
        # Get current sleep_at or raise error if not set
        current_sleep_at = getattr(self, 'sleep_at', None)
        if current_sleep_at is None:
            raise ValueError(
                'Cannot extend simulation: no sleep_at time is set. '
                'Use simulation.set_sleep_time() to set an initial sleep time.'
            )

        # Calculate new sleep_at: add 12 hours (legacy behavior)
        new_sleep_at = current_sleep_at + timedelta(hours=12)

        # Use v3 method to set sleep time (API will enforce constraints)
        self.set_sleep_time(new_sleep_at)

        return {
            'result': 'success',
            'message': new_sleep_at.isoformat(),
        }


class SimulationEndpointAPICompatMixin:
    """Mixin providing API-level backward compatibility for Simulation endpoints.

    This handles BC for API-level methods (create, list, patch, create_from, etc.)
    where v1/v2 used different parameter or field names than v3.
    """

    def patch(self, pk: PrimaryKey, **kwargs: Any) -> Simulation:
        """Patch a simulation with v1/v2 backward compatibility.

        Handles:
        - Boolean datetime fields (sleep, expires) → datetime fields
        - Field name mapping (see SimulationCompatMixin._FIELD_MAPPINGS)
        - Removed fields (see SimulationCompatMixin._REMOVED_FIELDS)
        - Routes OOB/NetQ fields to dedicated endpoints
        """
        handle_boolean_datetime_fields(
            kwargs, SimulationCompatMixin._BOOLEAN_DATETIME_FIELDS
        )
        drop_removed_fields(kwargs, SimulationCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, SimulationCompatMixin._FIELD_MAPPINGS)

        # Extract and route OOB/NetQ fields to dedicated endpoints
        # Note: NetQ depends on OOB, so we handle in this order:
        # 1. Disable NetQ (if needed)
        # 2. Enable/disable OOB
        # 3. Enable NetQ (if needed)
        auto_oob_enabled, disable_auto_oob_dhcp, auto_netq_enabled = (
            _extract_oob_netq_fields(kwargs)
        )

        # Step 1: Disable NetQ first (if disabling) since NetQ requires OOB
        if auto_netq_enabled is False:
            self.disable_auto_netq(simulation=pk)  # type: ignore[attr-defined]

        # Step 2: Handle OOB enable/disable
        if auto_oob_enabled is not None:
            if auto_oob_enabled:
                enable_kwargs = {}
                if disable_auto_oob_dhcp is not None:
                    enable_kwargs['disable_auto_oob_dhcp'] = disable_auto_oob_dhcp
                self.enable_auto_oob(simulation=pk, **enable_kwargs)  # type: ignore[attr-defined]
            else:
                self.disable_auto_oob(simulation=pk)  # type: ignore[attr-defined]

        # Step 3: Enable NetQ last (if enabling) since it requires OOB to be enabled
        if auto_netq_enabled is True:
            self.enable_auto_netq(simulation=pk)  # type: ignore[attr-defined]

        # Call parent patch for remaining fields, or get the simulation if no fields left
        if kwargs:
            return cast('Simulation', super().patch(pk, **kwargs))  # type: ignore[misc]
        else:
            # No fields left to patch, just return the updated simulation
            return cast('Simulation', self.get(pk))  # type: ignore[attr-defined]

    def list(self, *args: Any, **kwargs: Any) -> Any:
        """List simulations with v1/v2 filter name compatibility.

        Handles:
        - Field name mapping (see SimulationCompatMixin._FIELD_MAPPINGS)
        - Removed filters (see SimulationCompatMixin._REMOVED_FIELDS)
        """
        # Drop removed fields (includes both body fields and filters)
        drop_removed_fields(kwargs, SimulationCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, SimulationCompatMixin._FIELD_MAPPINGS)
        return super().list(*args, **kwargs)  # type: ignore[misc]

    def create_from(self, *args: Any, **kwargs: Any) -> Any:
        """Create simulation from topology data (v2 BC).

        v2's create_from only supported JSON format.
        For v1 DOT format support, use create(topology_data=...) instead.
        """
        # Map v1/v2 field names
        map_field_names(kwargs, SimulationCompatMixin._FIELD_MAPPINGS)

        # Extract format and content
        format_type = kwargs.pop('format', None)
        content = kwargs.pop('content', None)

        # Extract attempt_start
        attempt_start = kwargs.pop('attempt_start', False)

        if format_type is None or content is None:
            raise ValueError("'format' and 'content' parameters are required")

        # Normalize format to uppercase
        format_upper = format_type.upper()

        # v2 create_from only supported JSON
        if format_upper != 'JSON':
            raise ValueError(
                f"create_from only supports format='JSON'. Got: '{format_type}'. "
                f'For DOT format, use import_from_dot() instead.'
            )

        # Build a manifest and pass to import_from_simulation_manifest
        # This lets the v3 method handle all file/path/string resolution
        simulation_manifest = {'format': format_upper, 'content': content, **kwargs}
        return self.import_from_simulation_manifest(  # type: ignore[attr-defined]
            simulation_manifest=simulation_manifest,
            attempt_start=attempt_start,
        )

    def create(self, *args: Any, **kwargs: Any) -> Any:
        """Create a simulation with v1/v2 backward compatibility.

        v1 BC: If 'topology' or 'topology_data' is provided, redirects to create_from()
        v2 BC: Maps field names and drops fields not supported in v3
        """
        # Clean up kwargs for v3 (do this once at the start)
        handle_boolean_datetime_fields(
            kwargs, SimulationCompatMixin._BOOLEAN_DATETIME_FIELDS
        )
        drop_removed_fields(kwargs, SimulationCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, SimulationCompatMixin._FIELD_MAPPINGS)

        # v1 BC: topology/topology_data → create_from()
        if 'topology' in kwargs or 'topology_data' in kwargs:
            # v1 used topology_data in DOT format
            content = kwargs.pop('topology_data', None)
            topology_id = kwargs.pop('topology', None)

            if topology_id:
                # v1 accepted topology ID - not supported in v3
                raise ValueError(
                    'Creating simulation from topology ID is not supported in '
                    'current air-api version. Use create_from() with topology '
                    'data instead.'
                )

            if content:
                # v1/v2: Handle topology_data_type parameter
                # v1/v2 only supported DOT format in create(topology_data=...)
                # (other formats like collectx, ibdiagnet2 are not supported in v3)
                if 'topology_data_type' in kwargs:
                    topology_data_type = kwargs.pop('topology_data_type').lower()
                    # Only DOT is supported in v3, other formats are not supported
                    if topology_data_type != 'dot':
                        raise ValueError(
                            f"topology_data_type '{topology_data_type}' is not "
                            f"supported in current air-api version. Only 'dot' is "
                            f'supported. For JSON format, use create_from() instead.'
                        )

                # v1/v2 create(topology_data=...) always used DOT format
                warnings.warn(
                    'create(topology_data=...) is deprecated. '
                    'Use import_from_dot(topology_data=...) instead.',
                    category=DeprecationWarning,
                    stacklevel=2,
                )
                return self.import_from_dot(topology_data=content, **kwargs)  # type: ignore[attr-defined]

        # Extract attempt_start for native create path
        # (v3 create endpoint doesn't support it)
        attempt_start = kwargs.pop('attempt_start', False)

        # Create the simulation
        sim = super().create(*args, **kwargs)  # type: ignore[misc]

        # If attempt_start, wait for simulation to be ready and start it
        # (uses default timeout from _wait_and_start_simulation)
        if attempt_start:
            self._wait_and_start_simulation(sim)  # type: ignore[attr-defined]

        return sim

    # v1 API method aliases (deprecated)

    @deprecated('get_simulations() is deprecated. Use list() instead.')
    def get_simulations(self) -> Any:
        """List all simulations (v1 backward compatibility)."""
        return self.list()

    @deprecated('get_simulation() is deprecated. Use get() instead.')
    def get_simulation(self, simulation_id: str) -> Any:
        """Get a simulation by ID (v1 backward compatibility).

        Args:
            simulation_id: The simulation ID.

        Returns:
            Simulation object.

        Deprecated: Use get() instead.
        """
        return self.get(simulation_id)  # type: ignore[attr-defined]

    @deprecated('create_simulation() is deprecated. Use create() instead.')
    def create_simulation(self, **kwargs: Any) -> Any:
        """Create a simulation (v1 backward compatibility).

        Args:
            **kwargs: Simulation parameters.

        Returns:
            Created Simulation object.

        Deprecated: Use create() instead.
        """
        return self.create(**kwargs)

    @deprecated('update_simulation() is deprecated. Use get() then update() instead.')
    def update_simulation(self, simulation_id: str, data: dict[str, Any]) -> None:
        """Update a simulation (v1 backward compatibility).

        Args:
            simulation_id: The simulation ID.
            data: Dictionary of fields to update.

        Deprecated: Use get() then update() instead.
        """
        sim = self.get(simulation_id)  # type: ignore[attr-defined]
        sim.update(**data)

    @deprecated('duplicate() is deprecated. Use clone() instead.')
    def duplicate(self, *, simulation: Any, **kwargs: Any) -> Any:
        """Duplicate a simulation (v1/v2 backward compatibility).

        Args:
            simulation: Simulation object or simulation ID.
            **kwargs: Additional parameters (e.g., start).

        Returns:
            New duplicated Simulation object.

        Note:
            v1/v2 'start' parameter is mapped to v3 'attempt_start'.

        Deprecated: Use clone() instead.

        Example:
            >>> # v1/v2 style (still supported)
            >>> new_sim = api.simulations.duplicate(simulation=sim)
            >>> new_sim = api.simulations.duplicate(simulation=sim_id, start=True)

            >>> # v3 style (recommended)
            >>> new_sim = api.simulations.clone(simulation=sim)
            >>> new_sim = api.simulations.clone(simulation=sim, attempt_start=True)
        """
        # Apply field mappings (including start → attempt_start)
        map_field_names(kwargs, SimulationCompatMixin._FIELD_MAPPINGS)

        return self.clone(simulation=simulation, **kwargs)  # type: ignore[attr-defined]
