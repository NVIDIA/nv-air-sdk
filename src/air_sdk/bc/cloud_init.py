# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.types import NodeAssignmentDataV2, NodeAssignmentDataV3, UserConfigType
from air_sdk.utils import join_urls, raise_if_invalid_response, validate_payload_types

if TYPE_CHECKING:
    from typing import Iterable

    from air_sdk.endpoints import Node
    from air_sdk.endpoints.simulations import Simulation
    from air_sdk.endpoints.user_configs import UserConfig


@dataclass(eq=False)
class CloudInit(AirModelCompatMixin, AirModel):
    """Backwards compatibility for CloudInit model (v2 API).

    Handles v2 → v3 field changes:
    - simulation_node → node (field mapping)
    """

    node: Node = field(metadata=AirModel.FIELD_FOREIGN_KEY)
    user_data: UserConfig | None = field(
        metadata=AirModel.FIELD_FOREIGN_KEY, default=None, repr=False
    )
    user_data_name: str | None = field(default=None)
    meta_data: UserConfig | None = field(
        metadata=AirModel.FIELD_FOREIGN_KEY, default=None, repr=False
    )
    meta_data_name: str | None = field(default=None)

    @classmethod
    def get_model_api(cls) -> type[CloudInitEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model."""
        return CloudInitEndpointAPI

    @property
    def model_api(self) -> CloudInitEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)

    # Field name mappings from v2 to v3
    _FIELD_MAPPINGS = {
        'simulation_node': 'node',
    }

    @property
    def primary_key_field(self) -> str:
        """v2 compatibility: primary key field name."""
        return 'node'

    @property
    def __pk__(self) -> str:
        """v2 compatibility: primary key value."""
        # Access via the mapped field name
        node_value = self.__getattribute__('node')
        if hasattr(node_value, '__pk__'):
            return str(getattr(node_value, '__pk__'))
        if hasattr(node_value, 'id'):
            return str(getattr(node_value, 'id'))
        return '' if node_value is None else str(node_value)

    def full_update(
        self,
        user_data: UserConfigType = None,
        meta_data: UserConfigType = None,
    ) -> None:
        """Update all fields of the cloud-init assignment (v2 compatibility)."""
        assignments: list[NodeAssignmentDataV3] = [
            {
                'node': self.node,
                'user_data': user_data,
                'meta_data': meta_data,
            }
        ]
        self.node.simulation.node_bulk_assign(nodes=assignments)


class CloudInitEndpointAPI(BaseEndpointAPI[CloudInit]):
    """Backwards compatibility for CloudInitEndpointAPI.

    This mixin provides v2-style methods that delegate to the new v3 API.
    Handles conversion of v2 format to v3 format for bulk_assign operations.
    """

    model = CloudInit

    def _get_simulation_from_node(self, node: Node | PrimaryKey) -> Simulation:
        """Helper to fetch node and extract simulation ID.

        Args:
            node_id: The ID of the node to fetch
            operation_context: Description of the operation for error message

        Returns:
            The simulation object (AirModel or UUID string)

        Raises:
            ValueError: If simulation cannot be determined from node
        """
        from air_sdk.endpoints import Node

        if isinstance(node, Node):
            resolved_node = node
        else:
            resolved_node = node = self.__api__.nodes.get(node)
        return resolved_node.simulation

    def _convert_v2_to_v3_assignment(
        self, assignment: NodeAssignmentDataV2
    ) -> NodeAssignmentDataV3:
        """Convert a single v2 assignment to v3 format."""
        # Extract node ID
        simulation_node = assignment.get('simulation_node')
        if simulation_node is None:
            raise ValueError('simulation_node field is required in v2 format')

        # Create a new assignment with the node ID and the remaining fields
        v3_assignment: NodeAssignmentDataV3 = {
            **{
                key: value  # type: ignore[typeddict-item]
                for key, value in assignment.items()
                if key != 'simulation_node'
            },
            'node': simulation_node,
        }
        return v3_assignment

    def _group_assignments_by_simulation(
        self, assignments: list[NodeAssignmentDataV3]
    ) -> dict[str, list[NodeAssignmentDataV3]]:
        """Group assignments by their simulation ID.

        Fetches each node to determine its simulation and groups accordingly.
        """
        assignments_by_sim: dict[str, list[NodeAssignmentDataV3]] = dict()

        for assignment in assignments:
            node_id = assignment['node']
            simulation = self._get_simulation_from_node(node_id)

            # Extract the ID from the Simulation object or UUID
            if hasattr(simulation, 'id'):
                simulation_id = str(simulation.id)
            else:
                simulation_id = str(simulation)

            assignments_by_sim.setdefault(simulation_id, list()).append(assignment)

        return assignments_by_sim

    def _bulk_assign_across_simulations(
        self, assignments: list[NodeAssignmentDataV3]
    ) -> None:
        """Bulk assign when no simulation context - route to simulation-specific APIs."""
        assignments_by_sim = self._group_assignments_by_simulation(assignments)

        for simulation_id, sim_assignments in assignments_by_sim.items():
            self.__api__.simulations.node_bulk_assign(
                simulation=simulation_id, nodes=sim_assignments
            )

    @staticmethod
    def _resolve_forward_refs() -> None:
        """Resolve forward references for get_type_hints() at runtime.

        This is called lazily to avoid circular imports during module initialization.
        """
        if 'Node' not in globals():
            from air_sdk.endpoints.nodes import Node

            globals()['Node'] = Node
        if 'UserConfig' not in globals():
            from air_sdk.endpoints.user_configs import UserConfig

            globals()['UserConfig'] = UserConfig

    def get(self, pk: str, **params: Any) -> CloudInit:
        """Get cloud-init assignment by node ID (v2 compatibility).

        In v2 API, get() took a node ID and returned its cloud-init assignment.
        This is maintained for backwards compatibility.
        """
        self._resolve_forward_refs()
        node_id = str(pk)
        node_response = self.__api__.client.get(
            join_urls(self.__api__.nodes.url, node_id)
        )
        raise_if_invalid_response(
            node_response, status_code=HTTPStatus.OK, data_type=None
        )
        cloud_init = self.load_model(
            node_response.json()['cloud_init'] | {'node': node_id}
        )
        return cloud_init

    def patch(self, pk: PrimaryKey, **kwargs: Any) -> Any:
        """Update cloud-init assignment by node ID (v2 compatibility).

        In v2 API, patch() took a node ID and updated its cloud-init assignment.
        This is maintained for backwards compatibility.
        """
        node_id = str(pk)
        node = self.__api__.nodes.get(node_id)

        # Extract assignment keys present in kwargs
        # Use bulk_assign to update
        # Pass objects directly - serialize_payload will extract IDs
        assignment: NodeAssignmentDataV3 = {
            **kwargs,  # type: ignore[typeddict-item]
            'node': node_id,
        }
        assignments: list[NodeAssignmentDataV3] = [assignment]
        node.simulation.node_bulk_assign(nodes=assignments)

        # Call an explicit GET on the assignment so the node would be
        # refetched and the response edge cases handled
        return self.get(node_id)

    @validate_payload_types
    def bulk_assign(self, assignments: Iterable[NodeAssignmentDataV2]) -> None:
        """
        Bulk assign cloud-init assignments to nodes in multiple simulations.

        This is a v2 API compatibility layer around the v3 node assignment API.
        """
        v3_assignments = [
            self._convert_v2_to_v3_assignment(assignment) for assignment in assignments
        ]
        self._bulk_assign_across_simulations(v3_assignments)
