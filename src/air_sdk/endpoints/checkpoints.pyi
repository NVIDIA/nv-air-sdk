# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, Literal

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey

@dataclass(eq=False)
class Checkpoint(AirModel):
    """Checkpoint model representing a snapshot of a simulation run.

    Checkpoints are created when a simulation is shut down (stored). They
    capture the state of all nodes at that point in time and can be used
    to restore the simulation to that state later.

    Attributes:
        id: Unique identifier for the checkpoint
        name: A customizable name for the checkpoint
        created: Timestamp when the checkpoint was created
        modified: Timestamp when the checkpoint was last modified
        run: UUID of the run during which the checkpoint was created
        state: Current state of the checkpoint (PENDING, COMPLETE, or DELETED)
        favorite: Whether the checkpoint is favored over others when Air
                  determines which checkpoints should be automatically deleted
    """

    id: str
    name: str
    favorite: bool
    created: datetime
    modified: datetime
    run: str
    state: Literal['PENDING', 'COMPLETE', 'DELETED']

    @classmethod
    def get_model_api(cls) -> type[CheckpointEndpointAPI]: ...
    def update(
        self,
        *,
        name: str = ...,
        favorite: bool = ...,
        **kwargs: Any,
    ) -> None:
        """Update the checkpoint's properties.

        Args:
            name: A new name for the checkpoint
            favorite: Whether the checkpoint should be protected from
                      automatic deletion
            **kwargs: Additional fields for future API compatibility

        Example:
            >>> checkpoint.update(name='Before upgrade', favorite=True)
        """
        ...

    def delete(self) -> None:
        """Delete this checkpoint.

        Only checkpoints in the ``COMPLETE`` state may be deleted. Deletion
        updates the state to ``DELETED`` and removes the stored snapshots.

        Example:
            >>> checkpoint.delete()
        """
        ...

class CheckpointEndpointAPI(BaseEndpointAPI[Checkpoint]):
    """Endpoint API for managing simulation checkpoints.

    Provides methods for listing, retrieving, updating, and deleting
    checkpoints. Checkpoints cannot be created directly; they are
    created automatically when a simulation is shut down.
    """

    API_PATH: str
    model: type[Checkpoint]

    def list(
        self,
        *,
        simulation: str | PrimaryKey = ...,
        run: str | PrimaryKey = ...,
        state: Literal['PENDING', 'COMPLETE', 'DELETED'] = ...,
        favorite: bool = ...,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
        **kwargs: Any,
    ) -> Iterator[Checkpoint]:
        # fmt: off
        """List checkpoints.

        When accessed via ``simulation.checkpoints.list()``, results are
        automatically filtered to that simulation. When accessed via
        ``api.checkpoints.list()``, all visible checkpoints are returned
        unless filtered.

        Args:
            simulation: Filter by simulation UUID
            run: Filter by run UUID
            state: Filter by checkpoint state
            favorite: Filter by favorite status
            limit: Number of results to return per page
            offset: Initial index from which to return results
            ordering: Order by field (prefix with "-" for descending).
                      Options: created, modified, name, run, state, favorite
            search: Search by name or state
            **kwargs: Additional filter parameters

        Returns:
            Iterator of Checkpoint instances

        Example:
            >>> for cp in api.checkpoints.list(
            ...     simulation='sim-id', state='COMPLETE'
            ... ):
            ...     print(cp.name)
        """
        ...
        # fmt: on
    def get(self, pk: PrimaryKey, **kwargs: Any) -> Checkpoint:
        """Retrieve a specific checkpoint.

        Args:
            pk: Checkpoint UUID
            **kwargs: Additional query parameters

        Returns:
            Checkpoint instance

        Example:
            >>> checkpoint = api.checkpoints.get('checkpoint-uuid')
            >>> print(checkpoint.name, checkpoint.state)
        """
        ...

    def patch(
        self,
        pk: PrimaryKey,
        *,
        name: str = ...,
        favorite: bool = ...,
        **kwargs: Any,
    ) -> Checkpoint:
        """Update individual fields of a checkpoint.

        Only ``name`` and ``favorite`` can be modified.

        Args:
            pk: Checkpoint UUID
            name: A new name for the checkpoint
            favorite: Whether the checkpoint should be protected from
                      automatic deletion
            **kwargs: Additional fields for future API compatibility

        Returns:
            Updated Checkpoint instance

        Example:
            >>> checkpoint = api.checkpoints.patch(  # fmt: skip
            ...     'checkpoint-uuid', name='Pre-upgrade snapshot'
            ... )
        """
        ...

    def delete(self, pk: PrimaryKey, **kwargs: Any) -> None:
        """Delete a checkpoint.

        Only checkpoints in the ``COMPLETE`` state may be deleted. Deletion
        updates the state to ``DELETED`` and removes the stored snapshots.

        Args:
            pk: Checkpoint UUID
            **kwargs: Additional parameters

        Example:
            >>> api.checkpoints.delete('checkpoint-uuid')
        """
        ...

    def update(
        self,
        *,
        checkpoint: Checkpoint | PrimaryKey,
        name: str = ...,
        favorite: bool = ...,
        **kwargs: Any,
    ) -> Checkpoint:
        """Update individual fields of a checkpoint.

        Only ``name`` and ``favorite`` can be modified.

        Args:
            checkpoint: Checkpoint instance or checkpoint UUID
            name: A new name for the checkpoint
            favorite: Whether the checkpoint should be protected from
                      automatic deletion
            **kwargs: Additional fields for future API compatibility

        Returns:
            Updated Checkpoint instance

        Example:
            >>> cp = api.checkpoints.get('checkpoint-uuid')
            >>> api.checkpoints.update(checkpoint=cp, name='Renamed', favorite=True)
        """
        ...
