# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from air_sdk import const
from air_sdk.bc.decorators import deprecated
from air_sdk.client import Client

__all__ = [
    'const',
    'AirApi',
    'Client',
    'AirModelAttributeError',
    # Type definitions for API payloads
    'DockerRunParameters',
    'DockerRunTmpfsParameter',
    'EmulationParams',
    'Platform',
    'ResourceBudgetUsage',
    'Resources',
    'SimState',
    # endpoints
    'ServiceAPI',
    'ServiceEndpointApi',
    'NodeApi',
    'NodeEndpointApi',
    'SimulationApi',
    'SimulationEndpointApi',
    'InterfaceApi',
    'InterfaceEndpointApi',
    'SimulationInterfaceApi',
    'SimulationNodeApi',
    'SystemEndpointAPI',
    'ImageApi',
    'ImageEndpointApi',
    'ImageShareEndpointAPI',
    'MarketplaceDemoEndpointAPI',
    'MarketplaceDemoApi',
    'MarketplaceDemoEndpointApi',
    'MarketplaceDemoTagEndpointAPI',
    'MarketplaceDemoTagApi',
    'SSHKey',
    'SSHKeyEndpointAPI',
    'Training',
    'TrainingEndpointAPI',
    'UserConfigAPI',
    'UserConfigEndpointApi',
    # Organization / Resource Budget endpoint
    'Organization',
    'OrganizationApi',
    'OrganizationEndpointAPI',
    'ResourceBudget',
    'ResourceBudgetEndpointAPI',
]


from importlib.metadata import PackageNotFoundError, version

from air_sdk.exceptions import AirError, AirModelAttributeError
from air_sdk.types import (
    DockerRunParameters,
    DockerRunTmpfsParameter,
    EmulationParams,
    Platform,
    ResourceBudgetUsage,
    Resources,
    SimState,
)

if TYPE_CHECKING:
    from air_sdk.bc import CloudInitEndpointAPI
    from air_sdk.endpoints import (
        FleetEndpointAPI,
        HistoryEndpointAPI,
        ImageEndpointAPI,
        ImageShareEndpointAPI,
        InterfaceEndpointAPI,
        ManifestEndpointAPI,
        MarketplaceDemoEndpointAPI,
        MarketplaceDemoTagEndpointAPI,
        NodeEndpointAPI,
        NodeInstructionEndpointAPI,
        OrganizationEndpointAPI,
        ServiceEndpointAPI,
        SimulationEndpointAPI,
        SSHKeyEndpointAPI,
        SystemEndpointAPI,
        TrainingEndpointAPI,
        UserConfigEndpointAPI,
        WorkerClientCertificateEndpointAPI,
        WorkerEndpointAPI,
        ZTPScriptEndpointAPI,
    )


try:
    __version__ = version('nvidia-air-sdk')
except PackageNotFoundError:
    # package is not installed
    __version__ = 'unknown'


class AirApi:
    def __init__(
        self,
        api_url: str = const.AIR_API_URL,
        authenticate: bool = True,
        api_key: str | None = None,
        username: str | None = None,  # BC parameter for BC init won't fail
        password: str | None = None,  # BC alias for api_key
        bearer_token: str | None = None,  # BC alias for api_key
        auto_patch: bool = True,  # BC: enable auto-patching on attribute changes
    ) -> None:
        """
        Initialize AirApi and optionally authenticate with a local NGC config.

        For cleaner initialization, consider using one of the factory methods:
        - AirApi.with_api_key()
        - AirApi.with_device_login()
        - AirApi.with_ngc_config()
        """
        self.client = Client(api_url)
        self.auto_patch = auto_patch
        if authenticate:
            # api_key, password, and bearer_token are all aliases for the same thing
            token = api_key or password or bearer_token
            if token:
                self.client.headers.update({'Authorization': f'Bearer {token}'})
            else:
                self.auth_with_ngc_config()

    @classmethod
    def with_api_key(
        cls, api_key: str, api_url: str = const.AIR_API_URL, auto_patch: bool = True
    ) -> 'AirApi':
        """Initialize API with an explicit NGC API Key.

        The `api_key` is also known as a Starfleet API Key, or 'SAK'.
        """
        instance = cls(api_url=api_url, authenticate=False, auto_patch=auto_patch)
        instance.client.headers.update({'Authorization': f'Bearer {api_key}'})
        return instance

    @classmethod
    def with_device_login(
        cls,
        email: str,
        org_num: str,
        api_url: str = const.AIR_API_URL,
        auto_patch: bool = True,
    ) -> 'AirApi':
        """Initialize API with device login authentication."""
        instance = cls(api_url=api_url, authenticate=False, auto_patch=auto_patch)
        instance.client.ngc_device_login(email, org_num)
        return instance

    @classmethod
    def with_ngc_config(
        cls, api_url: str = const.AIR_API_URL, auto_patch: bool = True
    ) -> 'AirApi':
        """Initialize API using NGC config for authentication."""
        return cls(api_url=api_url, authenticate=True, auto_patch=auto_patch)

    def auth_with_ngc_config(self) -> None:
        """Authenticate with a local NGC config.

        This method is called by the `AirApi` constructor if `authenticate` is `True`.
        """
        err_msg = (
            'No NGC API key found. Please run the CLI command `ngc config set` '
            'to set NGC API key on your local machine. Alternatively, '
            'use an AirApi.with_api_key(api_key) or '
            'AirApi.with_device_login(email, org_num) '
            'methods to explicitly authenticate your client.'
        )
        try:
            auto_sak = self.client.hunt_for_sak()
            if auto_sak:
                censored_sak = f'{"*" * (len(auto_sak) - 3)}{auto_sak[-3:]}'
                print(f'Using auto-detected SAK found at ~/.ngc/config: {censored_sak}')  # noqa: T201
                self.client.headers.update({'Authorization': f'Bearer {auto_sak}'})
            else:
                raise AirError(err_msg)
        except AirError:
            raise AirError(err_msg)

    @property
    def histories(self) -> HistoryEndpointAPI:
        from .endpoints import HistoryEndpointAPI

        return HistoryEndpointAPI(self)

    @property
    def images(self) -> ImageEndpointAPI:
        from .endpoints import ImageEndpointAPI

        return ImageEndpointAPI(self)

    @property
    def image_shares(self) -> ImageShareEndpointAPI:
        from .endpoints import ImageShareEndpointAPI

        return ImageShareEndpointAPI(self)

    @property
    def simulations(self) -> SimulationEndpointAPI:
        from .endpoints import SimulationEndpointAPI

        return SimulationEndpointAPI(self)

    @property
    def systems(self) -> SystemEndpointAPI:
        from .endpoints import SystemEndpointAPI

        return SystemEndpointAPI(self)

    @property
    def nodes(self) -> NodeEndpointAPI:
        from .endpoints import NodeEndpointAPI

        return NodeEndpointAPI(self)

    @property
    def interfaces(self) -> InterfaceEndpointAPI:
        from .endpoints import InterfaceEndpointAPI

        return InterfaceEndpointAPI(self)

    @property
    def breakouts(self) -> None:
        """Breakouts endpoint - not supported in current API version.

        Raises:
            NotImplementedError
        """
        raise NotImplementedError(
            'The breakouts endpoint is not supported in the current API version. '
            'Breakouts are now managed as interface actions. '
            'Use interface.breakout(split_count) to create breakouts, '
            'and interface.revert_breakout() to revert them.'
        )

    @property
    def services(self) -> ServiceEndpointAPI:
        from .endpoints import ServiceEndpointAPI

        return ServiceEndpointAPI(self)

    @property
    @deprecated('simulation_interfaces is deprecated. Use AirApi.interfaces instead.')
    def simulation_interfaces(self) -> InterfaceEndpointAPI:
        return self.interfaces

    @property
    def node_instructions(self) -> NodeInstructionEndpointAPI:
        from .endpoints import NodeInstructionEndpointAPI

        return NodeInstructionEndpointAPI(self)

    @property
    @deprecated('simulation_nodes is deprecated, use AirApi.nodes instead.')
    def simulation_nodes(self) -> NodeEndpointAPI:
        return self.nodes

    @property
    def ztp_scripts(self) -> ZTPScriptEndpointAPI:
        from .endpoints import ZTPScriptEndpointAPI

        return ZTPScriptEndpointAPI(self)

    @property
    def workers(self) -> WorkerEndpointAPI:
        from .endpoints import WorkerEndpointAPI

        return WorkerEndpointAPI(self)

    @property
    def worker_client_certificates(self) -> WorkerClientCertificateEndpointAPI:
        from .endpoints import WorkerClientCertificateEndpointAPI

        return WorkerClientCertificateEndpointAPI(self)

    @property
    def fleets(self) -> FleetEndpointAPI:
        from .endpoints import FleetEndpointAPI

        return FleetEndpointAPI(self)

    @property
    def marketplace_demos(self) -> MarketplaceDemoEndpointAPI:
        from .endpoints import MarketplaceDemoEndpointAPI

        return MarketplaceDemoEndpointAPI(self)

    @property
    def marketplace_demo_tags(self) -> MarketplaceDemoTagEndpointAPI:
        from .endpoints import MarketplaceDemoTagEndpointAPI

        return MarketplaceDemoTagEndpointAPI(self)

    @property
    def ssh_keys(self) -> SSHKeyEndpointAPI:
        from .endpoints import SSHKeyEndpointAPI

        return SSHKeyEndpointAPI(self)

    @property
    def trainings(self) -> TrainingEndpointAPI:
        from .endpoints import TrainingEndpointAPI

        return TrainingEndpointAPI(self)

    @property
    def manifests(self) -> ManifestEndpointAPI:
        from .endpoints import ManifestEndpointAPI

        return ManifestEndpointAPI(self)

    @property
    @deprecated(
        'The cloud_inits property is deprecated and left only for '
        'backwards compatibility. The correct way to interact with cloud-init '
        'is to use the bulk_assign property on the Simulation object.'
    )
    def cloud_inits(self) -> CloudInitEndpointAPI:
        """Cloud-init endpoint for V2 backwards compatibility."""
        from .bc import CloudInitEndpointAPI

        return CloudInitEndpointAPI(self)

    @property
    def user_configs(self) -> UserConfigEndpointAPI:
        from .endpoints import UserConfigEndpointAPI

        return UserConfigEndpointAPI(self)

    @property
    def organizations(self) -> OrganizationEndpointAPI:
        """Organization / Resource Budget endpoint."""
        from .endpoints import OrganizationEndpointAPI

        return OrganizationEndpointAPI(self)

    @property
    def resource_budgets(self) -> OrganizationEndpointAPI:
        """Resource Budget endpoint (alias for organizations)."""
        return self.organizations

    # Deprecated singular aliases (v1/v2 backward compatibility)
    # TODO: Remove these properties in a future major version

    @property
    @deprecated(
        'AirApi.simulation is deprecated and will be removed in a future version. '
        'Use AirApi.simulations instead.'
    )
    def simulation(self) -> SimulationEndpointAPI:
        """Deprecated alias for simulations (v1 backward compatibility)."""
        return self.simulations

    @property
    @deprecated(
        'AirApi.service is deprecated and will be removed in a future version. '
        'Use AirApi.services instead.'
    )
    def service(self) -> ServiceEndpointAPI:
        """Deprecated alias for services (v1 backward compatibility)."""
        return self.services

    def set_connect_timeout(self, t_delta: timedelta) -> None:
        self.client.connect_timeout = t_delta

    def set_read_timeout(self, t_delta: timedelta) -> None:
        self.client.read_timeout = t_delta

    def set_page_size(self, n: int) -> None:
        """Set the page size of paginated responses."""
        if isinstance(n, int) and n > 0:
            self.client.pagination_page_size = n
        else:
            raise AirError('Pagination page size must be a positive integer.')


# Backward compatibility aliases (defined after AirApi to avoid circular imports)
from air_sdk.endpoints import (  # noqa: E402
    ImageEndpointAPI,
    InterfaceEndpointAPI,
    MarketplaceDemoEndpointAPI,
    MarketplaceDemoTagEndpointAPI,
    NodeEndpointAPI,
    Organization,
    OrganizationEndpointAPI,
    ResourceBudget,  # alias for Organization
    ResourceBudgetEndpointAPI,  # alias for OrganizationEndpointAPI
    ServiceEndpointAPI,
    SimulationEndpointAPI,
    SSHKey,
    SSHKeyEndpointAPI,
    Training,
    TrainingEndpointAPI,
    UserConfigEndpointAPI,
)

SimulationApi = SimulationEndpointAPI  # v1 BC alias
SimulationEndpointApi = SimulationEndpointAPI  # v2 BC alias
ImageApi = ImageEndpointAPI  # v1 BC alias
ImageEndpointApi = ImageEndpointAPI  # v2 BC alias
ServiceAPI = ServiceEndpointAPI  # v1 BC alias
ServiceEndpointApi = ServiceEndpointAPI  # v2 BC alias
MarketplaceDemoApi = MarketplaceDemoEndpointAPI  # v1 BC alias
MarketplaceDemoEndpointApi = MarketplaceDemoEndpointAPI  # v2 BC alias
MarketplaceDemoTagApi = MarketplaceDemoTagEndpointAPI  # v1 BC alias
InterfaceApi = InterfaceEndpointAPI  # v1 BC alias
InterfaceEndpointApi = InterfaceEndpointAPI  # v2 BC alias
SimulationInterfaceApi = InterfaceEndpointAPI  # v1 BC alias
SSHKeyApi = SSHKeyEndpointAPI  # v1 BC alias
SimulationNodeApi = NodeEndpointAPI  # v1 BC alias
NodeEndpointApi = NodeEndpointAPI  # v2 BC alias
NodeApi = NodeEndpointAPI  # v1 BC alias
UserConfigAPI = UserConfigEndpointAPI  # v1 BC alias
UserConfigEndpointApi = UserConfigEndpointAPI  # v2 BC alias
OrganizationApi = OrganizationEndpointAPI  # v1 BC alias

# Main class backward compatibility alias
AirAPI = AirApi  # alias for current tests TODO: remove that after all tests are updated
