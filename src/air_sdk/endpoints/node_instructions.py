# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI
from air_sdk.bc import (
    BaseCompatMixin,
    NodeInstructionCompatMixin,
    NodeInstructionEndpointAPICompatMixin,
)
from air_sdk.endpoints import mixins
from air_sdk.endpoints.nodes import Node


class ShellData(TypedDict):
    commands: list[str]  # List of shell commands to execute


class _FileDataRequired(TypedDict):
    files: list[dict[str, str]]  # List of dicts with 'path' and 'content'


class FileData(_FileDataRequired, total=False):
    post_commands: list[str]  # Shell commands to run after creating files


class InitData(TypedDict):
    hostname: str  # The hostname to set for the node


class ShellDataResponse(ShellData):
    executor: Literal['shell']  # Executor type (added by API)


class FileDataResponse(_FileDataRequired, total=False):
    post_commands: list[str]  # Shell commands to run after creating files
    executor: Literal['file']  # Executor type (added by API)


class InitDataResponse(InitData):
    executor: Literal['init']  # Executor type (added by API)


@dataclass(eq=False)
class NodeInstruction(BaseCompatMixin, NodeInstructionCompatMixin, AirModel):
    id: str = field(repr=False)
    name: str
    node: Node = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    data: ShellDataResponse | FileDataResponse | InitDataResponse = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    state: str
    run_again_on_rebuild: bool = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type[NodeInstructionEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model"""
        return NodeInstructionEndpointAPI

    @property
    def model_api(self) -> NodeInstructionEndpointAPI:
        """The current model API instance."""
        return self.get_model_api()(self.__api__)


class NodeInstructionEndpointAPI(
    NodeInstructionEndpointAPICompatMixin,
    mixins.ListApiMixin[NodeInstruction],
    mixins.CreateApiMixin[NodeInstruction],
    mixins.GetApiMixin[NodeInstruction],
    mixins.PatchApiMixin[NodeInstruction],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[NodeInstruction],
):
    API_PATH = 'simulations/nodes/instructions/'
    model = NodeInstruction
