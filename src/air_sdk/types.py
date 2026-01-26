# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import inspect
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
    TypedDict,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

if TYPE_CHECKING:
    from air_sdk.air_model import PrimaryKey
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


def type_check(value: Any, expected_type: Type[Any]) -> bool:
    """Recursively check if the value matches the expected type."""
    if isinstance(expected_type, ForwardRef):
        expected_type = expected_type._evaluate(globals(), locals(), frozenset())

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
