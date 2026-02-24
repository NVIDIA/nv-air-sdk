# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""Backward compatibility for Node endpoint."""

from __future__ import annotations

import json
import warnings
from typing import TYPE_CHECKING, Any

from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.bc.decorators import deprecated
from air_sdk.bc.utils import drop_removed_fields, map_field_names
from air_sdk.types import NodeAssignmentDataV3
from air_sdk.utils import raise_if_invalid_response

if TYPE_CHECKING:
    from air_sdk.bc import CloudInit
    from air_sdk.endpoints.simulations import Simulation


def _map_features_field_to_advanced_field(kwargs: dict[str, Any]) -> None:
    """Map v1/v2 'features' field content to v3 'advanced' field.

    In v1/v2, 'features' was a JSON string containing 'tpm' and 'uefi'.
    In v3, 'advanced' is a dict containing 'boot', 'secureboot', 'cpu_mode',
    'cpu_options', 'uefi', 'nic_model'. This function extracts 'uefi' from
    features and maps it to the advanced dict, then converts features to a dict
    for field name mapping to handle the rename.

    Args:
        kwargs: Dictionary of keyword arguments to modify in-place.

    Raises:
        ValueError: If features JSON string is invalid.
    """
    if 'features' not in kwargs:
        return

    raw_features = kwargs['features']
    try:
        # Parse the features JSON string
        parsed_features = (
            json.loads(raw_features) if isinstance(raw_features, str) else raw_features
        )

        # Extract 'uefi' and 'tpm' from features
        # The field name mapping will handle renaming 'features' → 'advanced'
        if 'uefi' in parsed_features or 'tpm' in parsed_features:
            kwargs['features'] = {}
            if 'uefi' in parsed_features:
                kwargs['features']['uefi'] = parsed_features['uefi']
            if 'tpm' in parsed_features:
                kwargs['features']['tpm'] = parsed_features['tpm']
        else:
            kwargs.pop('features', None)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f'Invalid features JSON: {raw_features}') from e


class NodeCompatMixin(AirModelCompatMixin):
    """Mixin providing Node-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with node fields and methods from older SDK versions.

    Handles:
    - Field name mappings for reading/writing: os → image, original → id
    - v1/v2 update() method with field name mapping and features → advanced conversion
    - v1 BC methods: create_node_instruction(), create_instructions(),
        list_instructions(), delete_instructions()
    - v1 deprecated methods: control() (now delegates to reset/rebuild)
    - v2 deprecated methods: set_agent_key()

    Note:
        The interfaces property returns a filtered endpoint for node interfaces.
        For v2 compatibility, the property behaviors match v2 expectations.
    """

    # Field name mappings from v1/v2 to v3
    _FIELD_MAPPINGS = {
        'os': 'image',  # v1/v2 used os
        'features': 'advanced',
        'original': 'id',
        'simulation_id': 'simulation',
    }

    # Fields that were removed in v3
    _REMOVED_FIELDS = [
        'boot_group',
        'console_password',
        'console_port',
        'console_url',
        'console_username',
        'interfaces',
        'last_worker',
        'original',
        'serial_port',
        'simx_ipv4',
        'system',
        'topology',
        'version',
        'worker',
        'emulated',
    ]

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update method with field name compatibility for Nodes.

        Normalizes old (v1/v2) field names to v3 equivalents:
        - os → image
        - features → advanced

        Note:
            This method overrides the parent update() to provide field mapping.
            Removed fields are silently dropped to maintain compatibility.
        """
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(kwargs, self._REMOVED_FIELDS)
        _map_features_field_to_advanced_field(kwargs)
        map_field_names(kwargs, self._FIELD_MAPPINGS)

        # Call the parent update() method
        super().update(*args, **kwargs)  # type: ignore[misc]

    @deprecated(
        'create_node_instruction() is deprecated, use node.instructions.create() instead.'
    )
    def create_node_instruction(self, *args: Any, **kwargs: Any) -> Any:
        """v1 deprecated method: Create a node instruction.

        Note:
            This is a v1 backward compatibility method.

            v1 signature: create_node_instruction(executor, data, monitor=None)
            v3 signature: node_instructions.create(node=node.id, executor, data,0
            ...     name=None, run_again_on_rebuild=False)

            The v1 'monitor' parameter is not supported in v3 and will be
            ignored with a warning.

        Raises:
            NotImplementedError: Instructions endpoint is not yet implemented in v3.

        Example:
            ... v3 style (recommended)
            >>> node.instructions.create(executor='shell', data='echo hello')
        """
        return self.instructions.create(*args, **kwargs)

    @deprecated(
        'create_instructions() is deprecated, use node.instructions.create() instead.'
    )
    def create_instructions(self, *args: Any, **kwargs: Any) -> Any:
        """v1 BC method: Create instructions for the node's agent to execute.

        Note:
            This is a v1 backward compatibility method.

            v1 signature: create_instructions(data=..., executor=..., **kwargs)
            v3 signature: node_instructions.create(node=..., executor=..., data=..., ...)

            The v1 'monitor' parameter is not supported in v3 and will be passed
            through but may be ignored by the API.

        Example:
            >>> # v1 style (backward compatible)
            >>> node.create_instructions(data='echo foo', executor='shell')
            {'id': '67f73552-ffdf-4e5f-9881-aeae227604a3'}

            >>> # v3 style (recommended)
            >>> node.instructions.create(
            ...     executor='shell',
            ...     data={'commands': [['echo foo', ['echo bar']]}
            ... )
        """
        return self.instructions.create(*args, **kwargs)

    @deprecated(
        'list_instructions() is deprecated, use node.instructions.list() instead.'
    )
    def list_instructions(self, **kwargs: Any) -> Any:
        """v1 BC method: List all instructions for the node.

        Returns:
            list: List of NodeInstruction objects

        Note:
            This is a v1 backward compatibility method.

        Example:
            >>> # v1 style (backward compatible)
            >>> node.list_instructions()
            [{'id': '56abc69b-489f-429a-aed9-600f26afc956'},
             {'id': '7c9c3449-f071-4bbc-bb42-bef04e44d74e'}]

            >>> # v3 style (recommended)
            >>> node.instructions.list()
            [{'id': '56abc69b-489f-429a-aed9-600f26afc956'},
             {'id': '7c9c3449-f071-4bbc-bb42-bef04e44d74e'}]
        """
        return self.instructions.list(**kwargs)

    @deprecated(
        'delete_instructions() is deprecated, '
        'use node.delete_all_node_instructions() instead.'
    )
    def delete_instructions(self) -> None:
        """v1 BC method: Delete all instructions for the node.

        Note:
            This is a v1 backward compatibility method.

        Example:
            >>> # v1 style (backward compatible)
            >>> node.delete_instructions()

            >>> # v3 style (recommended) - delete individual instructions
            >>> node.delete_all_node_instructions()
        """
        self.delete_all_node_instructions()

    def set_agent_key(self, **kwargs: Any) -> None:
        """v2 deprecated method: Set the Air Agent key.

        Sets the Air Agent key for the node.

        Raises:
            NotImplementedError: This feature is not supported in the current
                AIR API version.
        """
        raise NotImplementedError(
            'The set_agent_key() method is not yet supported '
            'in the current AIR API version.'
        )

    def control(self, action: str, **kwargs: Any) -> Any:
        """v1 BC method: Sends a control command to the node.

        Sends a control command to the node (e.g., 'reset', 'rebuild').

        raises:
            NotImplementedError: This feature is not yet supported in the
                current AIR API version.

        """
        if action == 'reset':
            # v3-compatible reset call
            return self.reset(**kwargs)
        elif action == 'rebuild':
            # v3-compatible reset call
            return self.rebuild(**kwargs)
        else:
            raise NotImplementedError(
                f"The control action '{action}' is not yet supported in the "
                'current AIR API version.'
            )

    @property
    def cloud_init(self) -> CloudInit:
        """v2 backwards compatibility: cloud_init property.

        Returns:
            CloudInit object for this node.
        """
        from air_sdk.bc.cloud_init import CloudInitEndpointAPI

        return CloudInitEndpointAPI(self.__api__).get(self.id)

    def get_cloud_init_assignment(self) -> dict[str, Any]:
        """Returns cloud-init assignment for the node (V1 compatibility).

        Returns:
            Dictionary with cloud-init assignments for the node.

        Example:
            >>> node = api.nodes.get('node-id')
            >>> assignment = node.get_cloud_init_assignment()
            >>> print(assignment['user_data'])
        """
        # Fetch the node from the API to get fresh cloud_init data
        url = self.detail_url
        response = self.__api__.client.get(url)
        raise_if_invalid_response(response, data_type=dict)
        node_data = response.json()

        # Extract cloud_init from the response
        cloud_init_data = node_data.get('cloud_init', {}) or {}

        return {
            'user_data': cloud_init_data.get('user_data'),
            'meta_data': cloud_init_data.get('meta_data'),
        }

    def set_cloud_init_assignment(self, script_mapping: dict[str, Any]) -> dict[str, Any]:
        """Edits cloud-init script assignment for the node (V1 compatibility).

        Returns updated cloud-init assignment for the node.
        Any combination of script keys can be provided within `script_mapping`.
        Explicit `None` as a value for a key will clear the assignment for that script.

        Args:
            script_mapping: Dictionary with 'user_data' and/or 'meta_data' keys.
                           Values can be UserConfig objects, string IDs, or None to clear.

        Returns:
            Dictionary with updated cloud-init assignment data.

        Examples:
            # Only sets user-data
            >>> node.set_cloud_init_assignment({'user_data': script})

            # Sets user-data, clears assignment for meta-data
            >>> node.set_cloud_init_assignment({'user_data': script, 'meta_data': None})

            # Identical to node.get_cloud_init_assignment()
            >>> node.set_cloud_init_assignment({})
        """
        # Build assignment payload
        # If no assignment, just return current state
        assignment: NodeAssignmentDataV3 = {**script_mapping}  # type: ignore[typeddict-item]
        if not assignment:
            return self.get_cloud_init_assignment()

        # Use bulk_assign with single assignment
        assignment['node'] = self.id
        assignments: list[NodeAssignmentDataV3] = [assignment]

        # Determine simulation
        simulation: Simulation | None = getattr(self, 'simulation', None)
        if not simulation:
            raise ValueError(
                f'Could not determine simulation for node {self.id}. '
                'Please use simulation.node_bulk_assign() instead.'
            )

        # Bulk assign cloud-init assignment to the simulation
        simulation.node_bulk_assign(nodes=assignments)

        # Return updated assignment
        return self.get_cloud_init_assignment()


class NodeEndpointAPICompatMixin:
    """Mixin providing NodeEndpointAPI-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with endpoint API methods from older SDK versions.

    Handles:
    - Field name mappings in create(), list(), get(): os → image, topology → simulation,
      features → advanced
    - v2 BC: create(system=...) redirects to create_from_system_node()
    - v1 BC: get(simulation_id=...) deprecated parameter (warns but still works)
    - v1 deprecated method aliases:
        get_nodes(),
        update_simulation_node(),
        get_simulation_nodes()
    - v2 unsupported methods: bulk_update_state(), bulk_update_keydisk()
    """

    def create(self, *args: Any, **kwargs: Any) -> Any:
        """Create a node with v1/v2 backward compatibility.

        Maps field names from v1/v2 SDK:
        - os → image
        - features → advanced (JSON string with uefi → dict)

        v2 BC: If 'system' parameter is provided, redirects to create_from_system_node().

        Args:
            *args: Positional arguments passed to create.
            **kwargs: Keyword arguments including name, simulation, image, etc.

        Returns:
            Created Node object.

        Note:
            The 'system' parameter triggers a redirect to create_from_system_node()
            and is deprecated in favor of calling create_from_system_node() directly.
        """
        # v2 BC: If 'system' is provided and not None,
        # redirect to create_from_system_node() Check for 'system' BEFORE
        # dropping removed fields (since 'system' is in removed fields list)
        # Map content first (features->advanced), then field names
        _map_features_field_to_advanced_field(kwargs)
        map_field_names(kwargs, NodeCompatMixin._FIELD_MAPPINGS)
        drop_removed_fields(
            kwargs, NodeCompatMixin._REMOVED_FIELDS, exclude_fields=['system']
        )

        if 'system' in kwargs:
            system = kwargs.pop('system')
            if system is not None:
                # Warn about deprecated usage
                warnings.warn(
                    "Passing 'system' to create() is deprecated. "
                    'Use create_from_system_node() instead.',
                    DeprecationWarning,
                    stacklevel=2,
                )
                # Redirect to create_from_system_node endpoint
                return self.create_from_system_node(system_node=system, *args, **kwargs)  # type: ignore[attr-defined]

        return super().create(*args, **kwargs)  # type: ignore[misc]

    def list(self, *args: Any, **kwargs: Any) -> Any:
        """List nodes with v1/v2 backward compatibility.

        Maps filter field names from v1/v2 SDK:
        - os → image

        Args:
            *args: Positional arguments passed to list.
            **kwargs: Keyword arguments including filters.

        Returns:
            Paginated list of Node objects.
        """
        # Clean up kwargs for v3 compatibility
        map_field_names(kwargs, NodeCompatMixin._FIELD_MAPPINGS)
        drop_removed_fields(kwargs, NodeCompatMixin._REMOVED_FIELDS)
        return super().list(*args, **kwargs)  # type: ignore[misc]

    def get(self, *args: Any, **kwargs: Any) -> Any:
        """Get a node with v1 backward compatibility.

        In v1, the get() method accepted 'simulation_id' as a kwarg filter.
        However, since node IDs are globally unique, simulation_id is unnecessary.

        This method maintains v1 compatibility but warns users that simulation_id
        is redundant and should not be used.

        Args:
            *args: Positional arguments (node_id).
            **kwargs: Keyword arguments (may include deprecated simulation_id).

        Returns:
            Node object.

        Note:
            The simulation_id parameter is deprecated
            and will be removed in a future version.
        """
        if 'simulation_id' in kwargs:
            warnings.warn(
                "Passing 'simulation_id' to get() is unnecessary. "
                'Node IDs are globally unique - just use get(node_id). ',
                DeprecationWarning,
                stacklevel=2,
            )
            # Remove it entirely - don't pass it to v3 API
            kwargs.pop('simulation_id')

        return super().get(*args, **kwargs)  # type: ignore[misc]

    def patch(self, *args: Any, **kwargs: Any) -> Any:
        """Patch a node with v1/v2 backward compatibility.

        Maps field name mappings from v1/v2 SDK:
        - os → image
        - features → advanced
        """
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(kwargs, NodeCompatMixin._REMOVED_FIELDS)
        _map_features_field_to_advanced_field(kwargs)
        map_field_names(kwargs, NodeCompatMixin._FIELD_MAPPINGS)

        return super().patch(*args, **kwargs)  # type: ignore[misc]

    @deprecated('get_nodes() is deprecated, use list() instead.')
    def get_nodes(self, simulation_id: str = '', **kwargs: Any) -> Any:
        """Deprecated: Use list() instead.

        Lists nodes, optionally filtered by simulation.

        Args:
            simulation_id: Simulation ID to filter nodes (optional)
            **kwargs: Additional query parameters/filters

        Returns:
            List of Node objects

        .. deprecated::
            Use :meth:`list` instead. Example: nodes.list(simulation='sim-id')

        Example:
            >>> # v1 style (deprecated, still supported)
            >>> nodes = api.nodes.get_nodes(simulation_id='sim-id')

            >>> # v3 style (recommended)
            >>> nodes = api.nodes.list(simulation='sim-id')
        """
        return self.list(**kwargs)

    @deprecated(
        'update_simulation_node() is deprecated, use airApi.nodes.update(node) instead.'
    )
    def update_simulation_node(self, *args: Any, **kwargs: Any) -> None:
        """Deprecated: Use node.update() instead.

        Updates a simulation node with the provided data.

        Args:
            simulation_node_id: Node ID
            **kwargs: Keyword arguments including fields to update

        Returns:
            None

        .. deprecated::
            Use :meth:`get` to retrieve the node, then call :meth:`update` on it.

        Example:
            >>> # v1 style (deprecated, still supported)
            >>> api.nodes.update_simulation_node('node-id', {'name': 'new-name'})

            >>> # v3 style (recommended)
            >>> node = api.nodes.get('node-id')
            >>> node.update(name='new-name')
        """
        if 'simulation_node_id' in kwargs:
            kwargs['node'] = kwargs.pop('simulation_node_id')
        _map_features_field_to_advanced_field(kwargs)
        map_field_names(kwargs, NodeCompatMixin._FIELD_MAPPINGS)
        drop_removed_fields(kwargs, NodeCompatMixin._REMOVED_FIELDS)
        self.update(*args, **kwargs)  # type: ignore[attr-defined]

    @deprecated('get_simulation_nodes() is deprecated, use airApi.nodes.list() instead.')
    def get_simulation_nodes(self, **kwargs: Any) -> Any:
        """Deprecated: Use list() instead.

        Lists simulation nodes.

        Args:
            **kwargs: Query parameters/filters

        Returns:
            List of Node objects

        .. deprecated::
            Use :meth:`list` instead.

        Example:
            >>> # v1 style (deprecated, still supported)
            >>> nodes = api.nodes.get_simulation_nodes(simulation='sim-id')

            >>> # v3 style (recommended)
            >>> nodes = api.nodes.list(simulation='sim-id')
        """
        return self.list(**kwargs)

    # v2 unsupported methods

    def bulk_update_state(self, data: list[dict[str, Any]]) -> None:  # type: ignore[valid-type]
        """v2 deprecated method: Bulk update node states.

        Performs state updates of nodes in bulk (worker client method).

        Args:
            data: List of state update payloads

        Returns:
            None

        Note:
            This method is not yet supported in the current AIR API version.
            In v2, this was used by worker clients to perform bulk state updates.

        Raises:
            NotImplementedError: This feature is not supported in the current
                AIR API version.
        """
        raise NotImplementedError(
            'The bulk_update_state() method is not yet supported in the '
            'current AIR API version.'
        )

    def bulk_update_keydisk(self, data: list[dict[str, Any]]) -> None:  # type: ignore[valid-type]
        """v2 deprecated method: Bulk update node keydisks.

        Performs keydisk updates of nodes in bulk (worker client method).

        Args:
            data: List of keydisk update payloads

        Returns:
            None

        Note:
            This method is not yet supported in the current AIR API version.
            In v2, this was used by worker clients to perform bulk keydisk updates.

        Raises:
            NotImplementedError: This feature is not supported in the current
                AIR API version.
        """
        raise NotImplementedError(
            'The bulk_update_keydisk() method is not yet supported in the '
            'current AIR API version.'
        )
