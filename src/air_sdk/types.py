# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import inspect
import sys
import typing
from datetime import datetime
from enum import Enum
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    ForwardRef,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeAlias,
    TypedDict,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

if TYPE_CHECKING:
    from air_sdk.air_model import PrimaryKey
    from air_sdk.endpoints.interfaces import Interface
    from air_sdk.endpoints.nodes import Node
    from air_sdk.endpoints.user_configs import UserConfig

T = TypeVar('T')


# ============================================================================
# Simulation State Constants
# ============================================================================


class SimState(str, Enum):
    """Simulation state constants.

    Use these instead of raw strings for type safety and IDE autocomplete.

    Example:
        >>> from air_sdk import SimState
        >>> while sim.state != SimState.ACTIVE:
        ...     sleep(5)
        ...     sim.refresh()
    """

    CLONING = 'CLONING'
    CREATING = 'CREATING'
    IMPORTING = 'IMPORTING'
    INVALID = 'INVALID'
    INACTIVE = 'INACTIVE'
    REQUESTING = 'REQUESTING'
    PROVISIONING = 'PROVISIONING'
    PREPARE_BOOT = 'PREPARE_BOOT'
    BOOTING = 'BOOTING'
    ACTIVE = 'ACTIVE'
    PREPARE_SHUTDOWN = 'PREPARE_SHUTDOWN'
    SHUTTING_DOWN = 'SHUTTING_DOWN'
    SAVING = 'SAVING'
    PREPARE_TEARDOWN = 'PREPARE_TEARDOWN'
    TEARING_DOWN = 'TEARING_DOWN'
    DELETING = 'DELETING'
    PREPARE_PURGE = 'PREPARE_PURGE'
    PURGING = 'PURGING'
    DEMO = 'DEMO'
    TRAINING = 'TRAINING'
    PREPARE_REBUILD = 'PREPARE_REBUILD'
    REBUILDING = 'REBUILDING'


class InstructionExportChoice(str, Enum):
    """Which instructions to include when exporting a simulation.

    Passed as the ``include_instructions`` parameter to
    :meth:`Simulation.export`. Use these instead of raw strings for type
    safety and IDE autocomplete. The name matches the air-api
    ``InstructionExportChoice`` constant.

    Example:
        >>> from air_sdk import InstructionExportChoice
        >>> choice = InstructionExportChoice.REPEATABLE
        >>> export_data = sim.export(include_instructions=choice)
    """

    NONE = 'NONE'
    REPEATABLE = 'REPEATABLE'
    REPEATABLE_OR_NOT_READY = 'REPEATABLE_OR_NOT_READY'


DEMO_SIMULATION_STATE: TypeAlias = Literal['DEMO', 'CLONING', 'INVALID']


# ============================================================================
# Publish Access Record Constants
# ============================================================================

PAR_STATUS: TypeAlias = Literal[
    'PENDING',
    'PENDING_ELEVATION',
    'PENDING_RESTRICTION',
    'PENDING_UNPUBLISH',
    'PENDING_ALLOWLIST',
    'APPROVED_PENDING_IMAGE_PUBLISH',
    'APPROVED',
    'DENIED',
    'REMOVED',
    'CANCELLED',
]


# ============================================================================
# Access Request Constants
# ============================================================================

ACCESS_REQUEST_STATUS: TypeAlias = Literal[
    'REQUESTED',
    'GRANTED',
    'DENIED',
    'REVOKED',
    'CLOSED',
]


# ============================================================================
# Data Structure Types for API Payloads
# ============================================================================


class DockerRunTmpfsParameter(TypedDict):
    """Docker tmpfs mount configuration."""

    path: str
    size_gb: int


class DockerRunParameters(TypedDict):
    """Docker run parameters for simulator containers."""

    tmpfs: list[DockerRunTmpfsParameter]
    cap_add: list[str]
    devices: list[str]
    volumes: list[str]
    environment: dict[str, str]


class Resources(TypedDict):
    """Resource overhead for a simulator/platform."""

    cpu: int
    memory: int


class Platform(TypedDict):
    """Emulated platform configuration."""

    cpu: int
    memory: int
    default_port_type: str
    default_port_count: int
    port_count_options: list[int]


class EmulationParams(TypedDict):
    """Emulation parameters for a simulator/platform."""

    direct_link_emulation: bool
    max_network_pci: int


class PluginManifestSecret(TypedDict):
    """A named secret a simulator may request."""

    name: str
    path: str


UserConfigType = Optional[Union['UserConfig', 'PrimaryKey']]


class NodeAssignmentDataV2(TypedDict, total=False):
    """v2 bulk assignment payload format."""

    simulation_node: Union[Node, PrimaryKey]
    user_data: UserConfigType
    meta_data: UserConfigType


class NodeAssignmentDataV3(TypedDict, total=False):
    """v3 bulk assignment payload format."""

    node: Node | PrimaryKey
    user_data: UserConfig | PrimaryKey | None  # NotRequired
    meta_data: UserConfig | PrimaryKey | None  # NotRequired


class NodeResetPayload(TypedDict):
    """Payload for resetting a node."""

    id: Node | PrimaryKey


class NodeRebuildPayload(TypedDict):
    """Payload for rebuilding a node."""

    id: Node | PrimaryKey


class NodeManagementInterfaceInfo(TypedDict, total=False):
    """Per-interface management address info returned by the Node API.

    `ip` may be `None` when the interface opts out of OOB-managed DHCP
    while remaining wired to the leaf switch.
    """

    ip: str | None
    mac_address: str | None


class NodeBreakoutOptionInterface(TypedDict):
    """An interface a port currently carries, as listed in its breakout options.

    Attributes:
        id: The interface ID; pass it to a bulk breakout to change the port
        name: The interface name
    """

    id: str
    name: str


class NodeBreakoutOption(TypedDict):
    """How one physical port of a node is split, and how else it may be.

    Breakout options are a mapping keyed by each port's display name (e.g.
    'swp1'); this is the value. The key is a label, not an identifier.

    Attributes:
        split: The split factor the port is currently at (e.g. '1x', '4x')
        split_options: Every split factor the port supports, smallest first
        interfaces: The interfaces the port currently carries, in order
    """

    split: str
    split_options: list[str]
    interfaces: list[NodeBreakoutOptionInterface]


class InterfaceBreakoutEntry(TypedDict):
    """One port to re-split in a bulk breakout.

    Attributes:
        id: Any interface the port currently carries
        split: The split factor to move the port to (e.g. '4x'); the un-split
            factor (e.g. '1x') reverts it
    """

    id: Interface | PrimaryKey
    split: str


class ResourceBudgetUsage(TypedDict):
    """Current resource usage within an organization's budget.

    Attributes:
        cpu: Number of CPU cores currently in use
        memory: Memory currently in use, in MiB
        disk_storage: Disk storage currently in use, in GB
        image_storage: Image storage currently in use, in GB
        userconfigs: User configs content currently in use, in bytes
    """

    cpu: float
    memory: float
    disk_storage: float
    image_storage: int
    userconfigs: int


class OSImageManifestPlatform(TypedDict):
    """Per-model platform information and OS template pins."""

    platform_information_version: str | None
    os_template_version: str | None


class OSImageCapabilities(TypedDict, total=False):
    """OS image capability flags; key presence means supported."""

    vsock: dict[str, Any]


class _OSImageManifestSpecRequired(TypedDict):
    """Required fields for OSImageManifestSpec."""

    os_type: str


class OSImageManifestSpec(_OSImageManifestSpecRequired, total=False):
    """OS image manifest payload for `api.images.upload()` (no `image`)."""

    platforms: dict[str, OSImageManifestPlatform]
    capabilities: OSImageCapabilities
    os_template_partition: str | None


class HistoryEntry(TypedDict):
    """A single history entry from a resource's nested ``history`` endpoint.

    Read-only and immutable - returned by ``list_history()`` on simulations,
    images, and marketplace demos. This is distinct from the legacy ``History``
    model returned by the deprecated flat ``histories`` endpoint.

    Attributes:
        object_id: ID of the entity this entry is about (e.g. a simulation ID)
        model: Type of entity being tracked (e.g. 'simulation')
        created: When the entry was recorded
        actor: Email or identifier of the user who performed the action
        description: Human-readable description of what happened
        severity: Event severity. Values: 'INFO', 'ERROR'
        labels: Backend-assigned labels (e.g. 'publishing'), used for filtering
    """

    object_id: str
    model: str
    created: datetime
    actor: str
    description: str
    severity: str
    labels: list[str]


class HistoryFilters(TypedDict):
    """Distinct history filter values available for a single resource.

    Returned by the nested ``history-filters`` endpoint on a resource (e.g. a
    simulation, image, or marketplace demo). The values span all of that
    resource's history and are intended to populate filter dropdowns.

    Attributes:
        actors: Distinct actor values present on the resource's history entries
        severities: Distinct severity values (e.g. 'INFO', 'ERROR')
        labels: Distinct label values (e.g. 'publishing')
    """

    actors: list[str]
    severities: list[str]
    labels: list[str]


class SimRequiredResources(TypedDict):
    """Required resources for a simulation."""

    cpu: int | float
    memory: int | float
    storage: int | float
    compute_hours: float


class ZTPConfigs(TypedDict, total=False):
    """A simulation's ZTP configuration, keyed by OS type.

    Only the configured OS types are present.

    Attributes:
        cumulus: The Cumulus provisioning script.
        nvos: The NVOS ZTP configuration, a JSON object.
    """

    cumulus: str
    nvos: dict[str, Any]


class ZTPConfigsUpdate(TypedDict, total=False):
    """A change to a simulation's ZTP configuration, keyed by OS type.

    OS types left out are kept, and an OS type set to `None` is removed.

    Attributes:
        cumulus: The new Cumulus provisioning script, or None to remove it.
        nvos: The new NVOS ZTP configuration, a JSON object, or None to remove it.
    """

    cumulus: str | None
    nvos: dict[str, Any] | None


# ============================================================================
# Type Checking Utilities
# ============================================================================


def is_typeddict(type_: Type[Any]) -> bool:
    return hasattr(type_, '__required_keys__') and hasattr(type_, '__optional_keys__')


def union_args_are_optional(args: Tuple[Union[Any, Any], ...]) -> bool:
    return len(args) >= 2 and type(None) in args


def is_union(type_: Type[Any]) -> bool:
    return get_origin(type_) in (Union, UnionType)


def is_optional_union(type_: Type[Any]) -> bool:
    return is_union(type_) and union_args_are_optional(get_args(type_))


def get_optional_arg(optional_type: Type[T | None]) -> Type[T]:
    return next(arg for arg in get_args(optional_type) if arg is not type(None))  # type: ignore[no-any-return]


def get_list_arg(list_type: Type[List[T]]) -> Type[T]:
    return get_args(list_type)[0]  # type: ignore[no-any-return]


def is_typed_dict(expected_type: Type[Any]) -> bool:
    """Determine if the `expected_type` provided is a subclass of TypedDict."""
    return is_typeddict(expected_type)


def type_check_typed_dict(value: Any, expected_type: Type[Any]) -> bool:
    """Perform type checking when the expected_type is a subclass of TypedDict.

    This currently does not work if the expected_type is also a dataclass.
    """
    if not isinstance(value, dict):
        return False
    expected_keys = expected_type.__annotations__.keys()
    # Check all keys provided are defined within the expected_type TypedDict
    if not all(key in value for key in expected_keys):
        return False
    # Recursively check each key's value type
    return all(
        type_check(value[key], expected_type.__annotations__[key])
        for key in expected_keys
    )


# Prefer the public ``typing.evaluate_forward_ref`` (3.14+): the private
# ``ForwardRef._evaluate`` warns on every call there and is removed in 3.16. Earlier
# versions only have the private one, whose signature varies: ``recursive_guard`` must
# go by keyword, and ``type_params`` only where accepted, so probe for it once.
_TYPING_EVALUATE_FORWARD_REF = getattr(typing, 'evaluate_forward_ref', None)
_FORWARD_REF_EVALUATE_HAS_TYPE_PARAMS = (
    _TYPING_EVALUATE_FORWARD_REF is None
    and 'type_params' in inspect.signature(ForwardRef._evaluate).parameters
)


def _evaluate_forward_ref(ref: ForwardRef) -> Any:
    """Resolve a ``ForwardRef`` in a way that works across Python versions.

    Names resolve in the module the reference records (``TypedDict`` fields do, and
    callers resolving another module's annotation must set it), otherwise in this one.
    """
    # Python <= 3.13 resolves in that module even when handed a namespace, while 3.14
    # lets the namespace win, so pick it here to keep every version in step.
    module = sys.modules.get(ref.__forward_module__) if ref.__forward_module__ else None
    globalns = globals() if module is None else vars(module)
    if _TYPING_EVALUATE_FORWARD_REF is not None:
        return _TYPING_EVALUATE_FORWARD_REF(ref, globals=globalns, type_params=())
    kwargs: dict[str, Any] = {'recursive_guard': frozenset()}
    if _FORWARD_REF_EVALUATE_HAS_TYPE_PARAMS:
        kwargs['type_params'] = ()
    return ref._evaluate(globalns, None, **kwargs)


def type_check(value: Any, expected_type: Type[Any]) -> bool:
    """Recursively check if the value matches the expected type."""
    if isinstance(expected_type, ForwardRef):
        expected_type = _evaluate_forward_ref(expected_type)

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if origin is None:  # Base case
        if expected_type == Any:
            return True
        if is_typed_dict(expected_type):
            return type_check_typed_dict(value, expected_type)
        return isinstance(value, expected_type)

    if origin in (Union, UnionType):
        return any(type_check(value, arg) for arg in args)

    if origin is list:
        if not isinstance(value, list):
            return False
        if not args:  # We're already a list, so if not args then we're good
            return True
        return all(type_check(item, args[0]) for item in value)

    if origin is dict:
        if not isinstance(value, dict):
            return False
        if not args:  # We're already a dict, so if no args then we're good
            return True
        key_type, value_type = args
        if value_type == Any:
            return True

        return all(
            (
                (type_check(k, key_type) if key_type != Any else True)
                and (type_check(v, value_type) if value_type != Any else True)
            )
            for k, v in value.items()
        )

    if origin is Literal:
        return any(value == arg for arg in args)

    if inspect.isclass(origin):
        return isinstance(value, origin)

    return False
