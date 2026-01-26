# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Backward Compatibility Layer

This package provides mixins to maintain backward compatibility with v1 and v2
SDK methods.
Each endpoint that had methods in v1/v2 gets its own compat mixin.

Usage:
    from air_sdk.bc import BaseCompatMixin, SimulationCompatMixin

    class Simulation(BaseCompatMixin, SimulationCompatMixin, AirModel):
        # Modern v3 implementation
        pass
"""

from .base import BaseCompatMixin, BaseEndpointAPICompatMixin
from .cloud_init import CloudInit, CloudInitEndpointAPI
from .decorators import deprecated
from .image import ImageCompatMixin, ImageEndpointAPICompatMixin
from .interface import InterfaceCompatMixin, InterfaceEndpointAPICompatMixin
from .manifests import ManifestCompatMixin, ManifestEndpointAPICompatMixin
from .marketplace_demos import (
    MarketplaceDemoCompatMixin,
    MarketplaceDemoEndpointAPICompatMixin,
)
from .node import NodeCompatMixin, NodeEndpointAPICompatMixin
from .node_instruction import (
    NodeInstructionCompatMixin,
    NodeInstructionEndpointAPICompatMixin,
)
from .organization import (
    OrganizationCompatMixin,
    OrganizationEndpointAPICompatMixin,
)
from .service import ServiceCompatMixin, ServiceEndpointAPICompatMixin
from .simulation import SimulationCompatMixin, SimulationEndpointAPICompatMixin
from .user_config import UserConfigEndpointAPICompatMixin

__all__ = [
    'BaseCompatMixin',
    'NodeInstructionCompatMixin',
    'NodeInstructionEndpointAPICompatMixin',
    'BaseEndpointAPICompatMixin',
    'ServiceCompatMixin',
    'ServiceEndpointAPICompatMixin',
    'CloudInitEndpointAPI',
    'CloudInit',
    'SimulationCompatMixin',
    'SimulationEndpointAPICompatMixin',
    'NodeCompatMixin',
    'NodeEndpointAPICompatMixin',
    'ImageCompatMixin',
    'ImageEndpointAPICompatMixin',
    'ManifestCompatMixin',
    'ManifestEndpointAPICompatMixin',
    'MarketplaceDemoCompatMixin',
    'MarketplaceDemoEndpointAPICompatMixin',
    'InterfaceCompatMixin',
    'InterfaceEndpointAPICompatMixin',
    'UserConfigEndpointAPICompatMixin',
    'OrganizationCompatMixin',
    'OrganizationEndpointAPICompatMixin',
    'deprecated',
]
