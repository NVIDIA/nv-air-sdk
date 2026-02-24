# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT


__all__ = [
    'CloudInit',
    'CloudInitEndpointAPI',
    'Fleet',
    'FleetEndpointAPI',
    'History',
    'HistoryEndpointAPI',
    'Image',
    'ImageEndpointAPI',
    'ImageShareEndpointAPI',
    'Node',
    'NodeEndpointAPI',
    'NodeInstructionEndpointAPI',
    'NodeInstructionsEndpointApi',  # BC alias for v2
    'ServiceEndpointAPI',
    'ServiceAPI',  # BC alias for v1
    'ServiceEndpointApi',  # BC alias for v2
    'Simulation',
    'SimulationEndpointAPI',
    'InterfaceEndpointAPI',
    'ManifestEndpointAPI',
    'SimulationApi',  # BC alias for v1
    'SimulationEndpointApi',  # BC alias for v2
    'SimulationNodeApi',  # BC alias for v1
    'SystemEndpointAPI',
    'ImageApi',  # BC alias for v1
    'ImageEndpointApi',  # BC alias for v2
    'MarketplaceDemoEndpointAPI',
    'MarketplaceDemoApi',  # BC alias for v1
    'MarketplaceDemoEndpointApi',  # BC alias for v2
    'MarketplaceDemoTagEndpointAPI',
    'InterfaceApi',  # BC alias for v1
    'InterfaceEndpointApi',  # BC alias for v2
    'SimulationInterfaceApi',  # BC alias for v1
    'SSHKeyEndpointAPI',
    'Training',
    'TrainingEndpointAPI',
    'TrainingNGCData',
    'UserConfig',
    'UserConfigEndpointAPI',
    'UserConfigAPI',  # BC alias for v1
    'UserConfigEndpointApi',  # BC alias for v2
    'Worker',
    'WorkerClientCertificate',
    'WorkerEndpointAPI',
    'WorkerClientCertificateEndpointAPI',
    'Fleet',
    'History',
    'Image',
    'ImageShare',
    'Manifest',
    'Node',
    'NodeInstruction',
    'Service',
    'Simulation',
    'SSHKey',
    'System',
    'ZTPScript',
    'ZTPScriptEndpointAPI',
    'Interface',
    'mixins',
    'MarketplaceDemo',
    'MarketplaceDemoTag',
    'Organization',
    'OrganizationEndpointAPI',
    'ResourceBudget',
    'ResourceBudgetEndpointAPI',
]

from air_sdk.bc.cloud_init import CloudInit, CloudInitEndpointAPI
from air_sdk.endpoints import mixins
from air_sdk.endpoints.fleets import Fleet, FleetEndpointAPI
from air_sdk.endpoints.history import History, HistoryEndpointAPI
from air_sdk.endpoints.images import (
    Image,
    ImageEndpointAPI,
    ImageShare,
    ImageShareEndpointAPI,
)
from air_sdk.endpoints.interfaces import Interface, InterfaceEndpointAPI
from air_sdk.endpoints.manifests import Manifest, ManifestEndpointAPI
from air_sdk.endpoints.marketplace_demo_tags import (
    MarketplaceDemoTag,
    MarketplaceDemoTagEndpointAPI,
)
from air_sdk.endpoints.marketplace_demos import (
    MarketplaceDemo,
    MarketplaceDemoEndpointAPI,
)
from air_sdk.endpoints.node_instructions import (
    NodeInstruction,
    NodeInstructionEndpointAPI,
)
from air_sdk.endpoints.nodes import Node, NodeEndpointAPI
from air_sdk.endpoints.organizations import (
    Organization,
    OrganizationEndpointAPI,
)
from air_sdk.endpoints.services import Service, ServiceEndpointAPI
from air_sdk.endpoints.simulations import Simulation, SimulationEndpointAPI
from air_sdk.endpoints.ssh_keys import SSHKey, SSHKeyEndpointAPI
from air_sdk.endpoints.systems import System, SystemEndpointAPI
from air_sdk.endpoints.trainings import Training, TrainingEndpointAPI, TrainingNGCData
from air_sdk.endpoints.user_configs import UserConfig, UserConfigEndpointAPI
from air_sdk.endpoints.workers import (
    Worker,
    WorkerClientCertificate,
    WorkerClientCertificateEndpointAPI,
    WorkerEndpointAPI,
)
from air_sdk.endpoints.ztp_scripts import ZTPScript, ZTPScriptEndpointAPI

# Backward compatibility aliases
ServiceAPI = ServiceEndpointAPI  # v1
ServiceEndpointApi = ServiceEndpointAPI  # v2
SimulationApi = SimulationEndpointAPI  # v1
SimulationEndpointApi = SimulationEndpointAPI  # v2
SimulationNodeApi = NodeEndpointAPI  # v1
ImageApi = ImageEndpointAPI  # v1
ImageEndpointApi = ImageEndpointAPI  # v2
MarketplaceDemoApi = MarketplaceDemoEndpointAPI  # v1
MarketplaceDemoEndpointApi = MarketplaceDemoEndpointAPI  # v2
InterfaceApi = InterfaceEndpointAPI  # v1
InterfaceEndpointApi = InterfaceEndpointAPI  # v2
SimulationInterfaceApi = InterfaceEndpointAPI  # v1
NodeInstructionsEndpointApi = NodeInstructionEndpointAPI  # V2
UserConfigAPI = UserConfigEndpointAPI  # v1
UserConfigEndpointApi = UserConfigEndpointAPI  # v2
ResourceBudget = Organization  # alias
ResourceBudgetEndpointAPI = OrganizationEndpointAPI  # alias
