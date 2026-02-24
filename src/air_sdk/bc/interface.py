# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Interface-specific backward compatibility for v1/v2 SDK.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.bc.utils import drop_removed_fields

if TYPE_CHECKING:
    from air_sdk.endpoints.interfaces import Interface


class InterfaceCompatMixin(AirModelCompatMixin):
    """Mixin providing Interface-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with interface fields and methods from older
    SDK versions:
    - dropped fields: Various

    Removed fields are automatically handled by AirModelCompatMixin.
    """

    # Fields that were removed in v3
    _REMOVED_FIELDS = [
        'link_up',
        'internal_ipv4',
        'full_ipv6',
        'prefix_ipv6',
        'port_number',
        'simulation',
        'preserve_mac',
        'link',
        'url',
        'index',
        'link_id',
        'original',
        'services',
    ]

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update method with field name compatibility for Interfaces.

        Drops unsupported fields:
        - Fields in _REMOVED_FIELDS
        """
        # Clean up kwargs for v3 compatibility
        drop_removed_fields(kwargs, self._REMOVED_FIELDS)

        # Call the parent update() method
        super().update(*args, **kwargs)  # type: ignore[misc]

    @property
    def simulation(self) -> Any:
        """v1/v2 BC: Get simulation via interface → node → simulation chain.

        This property provides backward compatibility for v1/v2 code that
        accessed interface.simulation. In v3, simulation is derived from the
        interface relationship: interface.node → Node.simulation

        Returns:
            Simulation object

        Example:
            >>> simulation = interface.simulation
            >>> print(simulation.name)
        """
        return self.node.simulation


class InterfaceEndpointAPICompatMixin:
    """Mixin providing API-level backward compatibility for Interface endpoints.

    This handles BC for API-level methods (create, list etc.)
    where v1/v2 used different parameters than v3.
    """

    def create(self, *args: Any, **kwargs: Any) -> Interface:
        """Create an interface with v1/v2 field name compatibility."""
        # Clean up kwargs for v3 (do this once at the start)
        drop_removed_fields(kwargs, InterfaceCompatMixin._REMOVED_FIELDS)
        return super().create(*args, **kwargs)  # type: ignore[no-any-return, misc]

    def list(self, *args: Any, **kwargs: Any) -> Iterator[Interface]:
        """List interfaces with v1/v2 filter name compatibility.

        Handles:
        - Removed filters (see InterfaceCompatMixin._REMOVED_FIELDS)
        - Preserves 'simulation' filter for v3 compatibility
        """
        # Drop removed fields except 'simulation' (used as filter in v3)
        drop_removed_fields(
            kwargs, InterfaceCompatMixin._REMOVED_FIELDS, exclude_fields=['simulation']
        )
        return super().list(*args, **kwargs)  # type: ignore[no-any-return, misc]
