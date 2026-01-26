# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for node instructions endpoint type hints.
"""

from dataclasses import _MISSING_TYPE, dataclass
from datetime import datetime
from typing import Iterator, Literal, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.nodes import Node

# Input types (for creating instructions - without executor field)
class ShellData(TypedDict):
    """Data structure for shell executor type (input for create)."""

    commands: list[str]  # List of shell commands to execute

class _FileDataRequired(TypedDict):
    """Required fields for FileData."""

    files: list[dict[str, str]]  # List of dicts with 'path' and 'content'

class FileData(_FileDataRequired, total=False):
    """Data structure for file executor type (input for create).

    Required: files - List of file dicts, each with 'path' and 'content' keys.
    Optional: post_commands - Shell commands to run after creating files.
    """

    post_commands: list[str]  # Shell commands to run after creating files

class InitData(TypedDict):
    """Data structure for init executor type (input for create)."""

    hostname: str  # The hostname to set for the node

# Output types (returned from API - with executor field)
class ShellDataResponse(ShellData):
    """Data structure for shell executor type (returned from API)."""

    executor: Literal['shell']  # Executor type (added by API)

class FileDataResponse(_FileDataRequired, total=False):
    """Data structure for file executor type (returned from API).

    Required: files - List of file dicts, each with 'path' and 'content' keys.
    Optional: post_commands - Shell commands to run after creating files.
    Optional: executor - Executor type (added by API).
    """

    post_commands: list[str]  # Shell commands to run after creating files
    executor: Literal['file']  # Executor type (added by API)

class InitDataResponse(InitData):
    """Data structure for init executor type (returned from API)."""

    executor: Literal['init']  # Executor type (added by API)

@dataclass(eq=False)
class NodeInstruction(AirModel):
    """Node instruction model representing an automation instruction for a node.

    Node instructions are commands or automation scripts that can be executed
    on simulation nodes. They support various executors and can be configured
    to run again on rebuild.

    Attributes:
        id: Unique identifier for the node instruction
        name: Human-readable name of the node instruction
        node: Node this instruction belongs to
        data: Instruction data (ShellData, FileData, or InitData)
        created: Timestamp when the node instruction was created
        modified: Timestamp when the node instruction was last modified
        run_again_on_rebuild: Whether to re-run this instruction on simulation rebuild
        state: Execution state (e.g., 'pending', 'running', 'completed', 'failed')
    """

    id: str
    name: str
    node: Node
    data: ShellDataResponse | FileDataResponse | InitDataResponse
    created: datetime
    modified: datetime
    state: str
    run_again_on_rebuild: bool

    @classmethod
    def get_model_api(cls) -> type[NodeInstructionEndpointAPI]: ...
    @property
    def model_api(self) -> NodeInstructionEndpointAPI: ...
    def update(
        self,
        *,
        name: str | None = ...,
        run_again_on_rebuild: bool | None = ...,
    ) -> None:
        """Update the node instruction's properties.

        Args:
            name: New name for the node instruction
            run_again_on_rebuild: Whether to re-run the instruction on simulation rebuild

        Example:
            >>> instruction = api.node_instructions.get('instruction-id')
            >>> instruction.update(name='New Name', run_again_on_rebuild=True)
        """
        ...

    def delete(self) -> None:
        """Delete this instruction.

        Example:
            >>> instruction = api.node_instructions.get('instruction-id')
            >>> instruction.delete()
        """
        ...

class NodeInstructionEndpointAPI(BaseEndpointAPI[NodeInstruction]):
    """API client for node instructions endpoints."""

    API_PATH: str
    model: type[NodeInstruction]

    def create(
        self,
        *,
        node: str | PrimaryKey,
        executor: Literal['shell', 'init', 'file'],
        data: ShellData | FileData | InitData,
        name: str | None = ...,
        run_again_on_rebuild: bool | None = ...,
    ) -> NodeInstruction:
        """Create a new node instruction.

        Args:
            node: Node object or ID to execute the instruction on
            name: Name for the instruction
            executor: Type of executor ('shell', 'init', 'file')

            data: Instruction data/payload (executor-specific):

                ShellData - For 'shell' executor
                    Contains: 'commands' (list of shell commands)

                FileData - For 'file' executor
                    Contains: 'files' (list of dicts with 'path' and 'content')
                    Optional: 'post_commands' (shell commands to run after creating files)

                InitData - For 'init' executor
                    Contains: 'hostname' (hostname to set for the node)

            run_again_on_rebuild: Optional whether to run instruction again on rebuild

        Returns:
            The created NodeInstruction instance

        Example:
            >>> # Create shell instruction
            >>> instruction = api.node_instructions.create(
            ...     name='Setup Script',
            ...     node='node-id',
            ...     executor='shell',
            ...     data=ShellData(commands=['#!/bin/bash\\necho "Hello"']),
            ...     run_again_on_rebuild=True,
            ... )

            >>> # Create file instruction
            >>> instruction = api.node_instructions.create(
            ...     name='Install Package',
            ...     node='node-id',
            ...     executor='file',
            ...     data=FileData(
            ...         files=[{'path': 'package.txt', 'content': 'package=1.0.0'}],
            ...         post_commands=['#!/bin/bash\\necho "Hello"'],
            ...     ),
            ...     run_again_on_rebuild=True,
            ... )

            >>> # Create init instruction
            >>> instruction = api.node_instructions.create(
            ...     name='Initialize Environment',
            ...     node='node-id',
            ...     executor='init',
            ...     data=InitData(hostname='my-node'),
            ...     run_again_on_rebuild=True,
            ... )
        """
        ...

    def list(  # type: ignore[override]
        self,
        *,
        created_by_client: bool = ...,
        executor: Literal['shell', 'init', 'file'] = ...,
        name: str = ...,
        node: str = ...,
        run_again_on_rebuild: bool = ...,
        simulation: str = ...,
        state: str = ...,
        search: str = ...,
        ordering: str = ...,
        limit: int = ...,
        offset: int = ...,
    ) -> Iterator[NodeInstruction]:
        """List all node instructions.

        Args:
            created_by_client: Filter by created by client
            executor: Filter by executor ('shell', 'init', 'file')
            name: Filter by name
            node: Filter by node
            run_again_on_rebuild: Filter by run_again_on_rebuild
            simulation: Filter by simulation
            state: Filter by state
            search: Search by name
            ordering: Order by field
            limit: Limit the number of results
            offset: Offset the results

        Returns:
            Iterator of NodeInstruction instances

        Example:
            >>> # List all instructions for a node
            >>> for instruction in api.node_instructions.list(node='node-id'):
            ...     print(instruction.name)

            >>> # List with multiple filters
            >>> for instruction in api.node_instructions.list(
            ...     simulation='sim-id',
            ...     executor='shell',
            ...     state='complete',
            ...     ordering='-created',
            ... ):
            ...     print(instruction.name, instruction.state)
        """
        ...

    def get(self, pk: PrimaryKey) -> NodeInstruction:
        """Get a specific node instruction by ID.

        Args:
            pk: The node instruction ID (string or UUID)

        Returns:
            The NodeInstruction instance

        Example:
            >>> instruction = api.node_instructions.get('instruction-id')
            >>> print(instruction.name)
        """
        ...

    def patch(
        self,
        *,
        pk: PrimaryKey,
        name: str | None | _MISSING_TYPE = ...,
        run_again_on_rebuild: bool | None | _MISSING_TYPE = ...,
    ) -> NodeInstruction:
        # fmt: off
        """Partially update a node instruction.

        Args:
            pk: The node instruction ID
            name: New name for the instruction
            run_again_on_rebuild: Whether to run again on rebuild

        Returns:
            The updated NodeInstruction instance

        Example:
            >>> instruction = api.node_instructions.patch(
            ...     'instruction-id',
            ...     name='Updated Name',
            ...     run_again_on_rebuild=True
            ... )
        """
        # fmt: on
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """Delete a node instruction.

        Args:
            pk: The node instruction ID

        Example:
            >>> api.node_instructions.delete('instruction-id')
        """
        ...
