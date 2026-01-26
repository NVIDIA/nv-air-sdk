# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
"""Backward compatibility for Service endpoint."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.bc.decorators import deprecated
from air_sdk.bc.utils import drop_removed_fields, map_field_names

if TYPE_CHECKING:
    from air_sdk.air_model import PrimaryKey
    from air_sdk.endpoints.services import Service
    from air_sdk.endpoints.simulations import Simulation


class ServiceCompatMixin(AirModelCompatMixin):
    """Mixin providing Service-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with service fields from older SDK versions.

    Handles:
    - Field name mappings for reading/writing: dest_port → node_port,
      src_port → worker_port, host → worker_fqdn
    - Lazy-loading simulation property via interface → node → simulation chain

    Field mappings and removed fields are automatically handled by AirModelCompatMixin.

    Note:
        Services are immutable after creation in the Air API - no update support.
    """

    # Field name mappings from v1/v2 to v3
    _FIELD_MAPPINGS = {
        'dest_port': 'node_port',  # v1/v2 used dest_port
        'src_port': 'worker_port',  # v2 used src_port
        'host': 'worker_fqdn',  # v2 used host
        'simulation_id': 'simulation',  # v1/v2 used simulation_id in create_service()
    }

    # Fields that were removed in v3
    _REMOVED_FIELDS: list[str] = []

    @property
    def simulation(self) -> Any:
        """v1/v2 BC: Get simulation via interface → node → simulation chain.

        This property provides backward compatibility for v1/v2 code that accessed
        service.simulation. In v3, simulation is derived from the interface relationship:
        service.interface → Interface.node → Node.simulation


        Returns:
            Simulation object

        Example:
            >>> service.simulation.name
            'My Simulation'
        """
        # service.interface (FK) → interface.node (FK) → node.simulation (FK)
        return self.interface.node.simulation

    def update(self, **kwargs: Any) -> None:
        """Services are immutable - update is not supported.

        Raises:
            NotImplementedError: Services cannot be updated after creation.
                Delete the service and create a new one instead.
        """
        raise NotImplementedError(
            'Services are immutable after creation in the Air API. '
            'The update() method is not supported. '
            'To change a service, delete it and create a new one.'
        )


class ServiceEndpointAPICompatMixin:
    """Mixin providing ServiceEndpointAPI-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with endpoint API methods from older SDK versions.

    Handles:
    - Field name mappings: dest_port → node_port, src_port → worker_port,
      host → worker_fqdn
    - Deprecated method aliases: get_services(), get_service(), create_service()
    """

    def create(self, *args: Any, **kwargs: Any) -> Service:
        """Create a service with v1/v2 backward compatibility.

        Maps field names from v1/v2 SDK:
        - dest_port → node_port
        - src_port → worker_port
        - host → worker_fqdn

        Handles v1/v2 'node_name:interface_name' string format by resolving
        it to an interface ID using the provided simulation context.
        """
        drop_removed_fields(kwargs, ServiceCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, ServiceCompatMixin._FIELD_MAPPINGS)

        # v1/v2 BC: Handle 'node:interface' string format
        if (
            'interface' in kwargs
            and isinstance(kwargs['interface'], str)
            and ':' in kwargs['interface']
        ):
            # Extract simulation for scoped lookup
            simulation = kwargs.pop('simulation', None)
            if simulation is None:
                raise ValueError(
                    "Interface string format 'node_name:interface_name' requires "
                    'a simulation context. Please provide the simulation parameter.'
                )

            warnings.warn(
                "Using 'node:interface' string format is deprecated. "
                "Use sim.create_service(node_name='name', interface_name='name', ...) "
                'or provide an explicit interface ID.',
                DeprecationWarning,
                stacklevel=3,
            )

            kwargs['interface'] = self._resolve_interface_string(
                kwargs['interface'], simulation
            )
        else:
            # Remove simulation from kwargs if present (not an API parameter)
            # Note: v3 sim.services property passes this via default_filters
            # We silently remove it to avoid warnings for v3 users
            kwargs.pop('simulation', None)

        # Call parent create
        return super().create(*args, **kwargs)  # type: ignore[misc, no-any-return]

    def _resolve_interface_string(
        self, interface_str: str, simulation: Simulation | PrimaryKey
    ) -> str:
        """Resolve v1/v2 'node_name:interface_name' format to interface ID.

        Args:
            interface_str: Interface in format 'node_name:interface_name'
            simulation: Simulation ID or Simulation object to scope the search

        Returns:
            Interface ID

        Raises:
            ValueError: If format invalid or interface not found
        """
        # Ensure we have a Simulation object
        from air_sdk.endpoints.simulations import Simulation

        try:
            node_name, interface_name = interface_str.split(':', 1)
        except (ValueError, AttributeError):
            raise ValueError(
                '`interface` must be in the format "node_name:interface_name"'
            )

        sim: Simulation
        if isinstance(simulation, Simulation):
            sim = simulation
        else:
            sim = self.__api__.simulations.get(simulation)  # type: ignore[attr-defined]

        # Find the node by name within the simulation
        node_obj = next(sim.nodes.list(name=node_name), None)
        if not node_obj:
            raise ValueError(f'Node "{node_name}" not found in simulation "{sim.id}"')

        # Find the interface by name on the node
        interface_obj = next(
            self.__api__.interfaces.list(node=node_obj.id, name=interface_name),  # type: ignore[attr-defined]
            None,
        )
        if not interface_obj:
            raise ValueError(
                f'Interface "{interface_name}" not found on node "{node_name}"'
            )
        return str(interface_obj.id)

    def list(self, *args: Any, **kwargs: Any) -> Any:
        """List services with v1/v2 backward compatibility.

        Maps filter field names from v1/v2 SDK.
        """
        drop_removed_fields(kwargs, ServiceCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, ServiceCompatMixin._FIELD_MAPPINGS)

        # Call parent list
        return super().list(*args, **kwargs)  # type: ignore[misc]

    # v1 deprecated method aliases
    @deprecated('get_services() is deprecated, use list() instead.')
    def get_services(self, **kwargs: Any) -> Any:
        """Deprecated: Use list() instead.

        .. deprecated::
            Use :meth:`list` instead.
        """
        return self.list(**kwargs)

    @deprecated('get_service() is deprecated, use get() instead.')
    def get_service(self, service_id: str, **kwargs: Any) -> Service:
        """Deprecated: Use get() instead.

        .. deprecated::
            Use :meth:`get` instead.
        """
        return self.get(service_id, **kwargs)  # type: ignore[attr-defined, no-any-return]

    @deprecated('create_service() is deprecated, use create() instead.')
    def create_service(self, **kwargs: Any) -> Service:
        """Deprecated: Use create() instead.

        .. deprecated::
            Use :meth:`create` instead.
        """
        return self.create(**kwargs)
