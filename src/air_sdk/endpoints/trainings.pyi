# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

import builtins
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey
from air_sdk.endpoints.simulations import Simulation

class TrainingNGCData(TypedDict, total=False):
    """External user group data from NGC for a training event.

    This data is retrieved from the NGC API and includes information about
    the user group, its members, and invitation status.
    """

    userGroupId: str
    orgName: str
    resourceGroup: str
    name: str
    description: str
    idpListLocked: bool
    requireMatchingEmail: bool
    isUserGroupAdmin: bool
    serviceRoles: list[str]
    companyName: str
    groupContactEmail: str
    permissionSetDesc: str
    startDate: str
    endDate: str
    confirmedUsers: list[str]
    pendingInvitations: list[str]
    type: str

@dataclass(eq=False)
class Training(AirModel):
    """Training model representing a training event with NGC group and cloned simulation.

    Attributes:
        id: Unique identifier for the training event
        name: Name of the training event (also NGC user group name, must be kebab-case)
        created: Timestamp when the training was created
        modified: Timestamp when the training was last modified
        creator: Email of the client that created the training
        org: Organization UUID associated with this training
        training_simulation: Foreign key to template simulation (lazy loaded)
        training_simulation_name: Name of the training simulation (read-only)
        training_simulation_state: State of the training simulation (read-only)
        event_time: When the training event will occur (must be 5h+ in future)
        ngc_group_id: NGC external user group ID (must be kebab-case)
        attendees: List of validated attendee email addresses
        sim_start_time: When workbenches are created/started
                        (1h+ future, 4h before event_time)
        sim_end_time: When workbenches expire/destroyed (24h+ after event_time)
        workbenches_created: Whether workbenches have been created

    Timing Constraints:
        - event_time must be at least 5h in the future
        - sim_start_time must be at least 1h in the future and 4h before event_time
        - sim_end_time must be at least 24h after event_time

    Update Restrictions:
        Only event_time, sim_start_time, and sim_end_time can be updated.
        Name, parent simulation, checkpoint, and attendees cannot be
        modified after creation.

    Note:
        The training_simulation field is a lazy-loaded foreign key. Accessing it will
        automatically fetch the full Simulation object from the API.
    """

    @classmethod
    def get_model_api(cls) -> type[TrainingEndpointAPI]: ...

    id: str
    name: str
    created: datetime
    modified: datetime
    creator: str
    org: str
    training_simulation: Simulation
    training_simulation_name: str
    training_simulation_state: str
    event_time: datetime
    ngc_group_id: str
    sim_start_time: datetime
    sim_end_time: datetime
    attendees: list[str]
    workbenches_created: bool

    def update(
        self,
        *,
        event_time: datetime = ...,
        sim_start_time: datetime = ...,
        sim_end_time: datetime = ...,
        **kwargs: Any,
    ) -> None:
        # fmt: off
        """Update individual fields of the training event.

        Only event_time, sim_start_time, and sim_end_time can be updated.
        Name, parent simulation, checkpoint, and attendees cannot be modified
        via this endpoint after creation.

        Timing Constraints:
            - event_time: Must be at least 5h in the future
            - sim_start_time: Must be 1h+ in future and 4h before event_time
            - sim_end_time: Must be at least 24h after event_time

        Args:
            event_time: When the training event will occur
            sim_start_time: When workbenches are created/started
            sim_end_time: When workbenches expire/destroyed
            **kwargs: Additional fields for future API compatibility

        Raises:
            ValidationError: If timing constraints are violated

        Example:
            >>> training.update(
            ...     event_time=datetime(2026, 3, 15, 9, 0),
            ...     sim_start_time=datetime(2026, 3, 15, 5, 0),
            ...     sim_end_time=datetime(2026, 3, 16, 9, 0)
            ... )
        """
        ...
        # fmt: on
    def add_attendees(self, *, attendees: list[str], **kwargs: Any) -> None:
        # fmt: off
        """Add attendees to the training event.

        Args:
            attendees: List of email addresses to add as attendees
            **kwargs: Additional parameters

        Example:
            >>> training.add_attendees(
            ...     attendees=['user1@example.com', 'user2@example.com']
            ... )
        """
        ...
        # fmt: on
    def remove_attendees(self, *, attendees: list[str], **kwargs: Any) -> None:
        # fmt: off
        """Remove attendees from the training event.

        Args:
            attendees: List of email addresses to remove from attendees
            **kwargs: Additional parameters

        Example:
            >>> training.remove_attendees(
            ...     attendees=['user1@example.com']
            ... )
        """
        ...
        # fmt: on
    def get_external_user_group(self, **kwargs: Any) -> TrainingNGCData:
        """Get NGC external user group information.

        Makes an external API call to NGC to retrieve full details about the
        training's user group, including confirmed users and pending invitations.

        Args:
            **kwargs: Additional parameters

        Returns:
            NGC user group data including members and invitation status

        Example:
            >>> group_data = training.get_external_user_group()
            >>> print(f'Group: {group_data["name"]}')
            >>> print(f'Confirmed users: {group_data.get("confirmedUsers", [])}')
            >>> print(f'Pending invitations: {group_data.get("pendingInvitations", [])}')
        """
        ...

class TrainingEndpointAPI(BaseEndpointAPI[Training]):
    """Endpoint API for managing training events.

    Provides methods for listing, creating, retrieving, updating, and deleting
    training events, as well as managing attendees and retrieving NGC user group
    information.
    """

    API_PATH: str
    ATTENDEES_ADD_PATH: str
    ATTENDEES_REMOVE_PATH: str
    EXTERNAL_USER_GROUP_PATH: str
    model: type[Training]

    def list(
        self,
        *,
        limit: int = ...,
        name: str = ...,
        ngc_group_id: str = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
        training_simulation: str | PrimaryKey = ...,
        workbenches_created: bool = ...,
        **params: Any,
    ) -> Iterator[Training]:
        # fmt: off
        """List all training events.

        Args:
            limit: Number of results to return per page
            name: Filter by training name
            ngc_group_id: Filter by NGC external user group ID
            offset: Initial index from which to return results
            ordering: Order by field (prefix with "-" for desc). Options:
                      -created, -creator, -event_time, -modified, -name,
                      -ngc_group_id, -sim_end_time, -sim_start_time,
                      -training_simulation_name, -training_simulation_state,
                      -workbenches_created, created, creator, event_time,
                      modified, name, ngc_group_id, sim_end_time,
                      sim_start_time, training_simulation_name,
                      training_simulation_state, workbenches_created
            search: Search by name, creator, training_simulation_name,
                    training_simulation_state, event_time, sim_start_time,
                    sim_end_time, created
            training_simulation: Filter by template simulation ID
            workbenches_created: Filter by workbenches creation status
            **params: Additional filter parameters

        Returns:
            Iterator of Training instances

        Example:
            >>> for training in api.trainings.list():
            ...     print(training.name)
            >>> # Filter by name
            >>> trainings = api.trainings.list(name='network-training')
            >>> # Filter by simulation
            >>> trainings = api.trainings.list(training_simulation='sim-123')
        """
        ...
        # fmt: on
    def create(
        self,
        *,
        name: str,
        parent_simulation: str | PrimaryKey,
        attendees: builtins.list[str],
        event_time: datetime,
        sim_start_time: datetime,
        sim_end_time: datetime,
        parent_simulation_checkpoint: str | PrimaryKey = ...,
        **kwargs: Any,
    ) -> Training:
        # fmt: off
        """Create a new training event with NGC group and cloned simulation.

        The simulation will be cloned when creating the training. After cloning
        completes, the parent_simulation transitions to INACTIVE state and is no
        longer associated with the training. A dedicated training_simulation is
        created for the training session.

        Args:
            name: Name of the training event (must be kebab-case, used as NGC
                  user group name)
            parent_simulation: Simulation to clone for the training (transitions
                               to INACTIVE after cloning)
            attendees: List of attendee email addresses (required, case-sensitive,
                       no duplicates)
            event_time: When the training event will occur (must be 5h+ in future,
                        sim_end_time must be 24h+ after this)
            sim_start_time: When workbenches are created/started (must be 1h+ in
                            future and 4h before event_time)
            sim_end_time: When workbenches expire/destroyed (must be 24h+ after
                          event_time)
            parent_simulation_checkpoint: Checkpoint from parent_simulation to
                                          clone onto training_simulation (optional)
            **kwargs: Additional fields for future API compatibility

        Returns:
            Created Training instance

        Example:
            >>> training = api.trainings.create(
            ...     name='network-training-101',
            ...     parent_simulation='sim-id-123',
            ...     attendees=['student1@example.com', 'student2@example.com'],
            ...     event_time=datetime(2026, 3, 15, 9, 0),
            ...     sim_start_time=datetime(2026, 3, 15, 5, 0),
            ...     sim_end_time=datetime(2026, 3, 16, 9, 0)
            ... )
        """
        ...
        # fmt: on
    def get(self, pk: PrimaryKey, **params: Any) -> Training:
        """Retrieve a specific training event.

        Args:
            pk: Training ID
            **params: Additional query parameters

        Returns:
            Training instance

        Example:
            >>> training = api.trainings.get('training-id-123')
            >>> print(training.name)
        """
        ...

    def patch(
        self,
        pk: PrimaryKey,
        *,
        event_time: datetime = ...,
        sim_start_time: datetime = ...,
        sim_end_time: datetime = ...,
        **kwargs: Any,
    ) -> Training:
        # fmt: off
        """Update individual fields of a training event.

        Only event_time, sim_start_time, and sim_end_time can be updated.

        Args:
            pk: Training ID
            event_time: When the training event will occur
            sim_start_time: When workbenches are created/started
            sim_end_time: When workbenches expire/destroyed
            **kwargs: Additional fields for future API compatibility

        Returns:
            Updated Training instance

        Example:
            >>> training = api.trainings.patch(
            ...     'training-id-123',
            ...     event_time=datetime(2026, 3, 15, 9, 0),
            ... )
        """
        ...
        # fmt: on
    def delete(self, pk: PrimaryKey, **kwargs: Any) -> None:
        """Delete a training event and its associated NGC user group.

        Args:
            pk: Training ID
            **kwargs: Additional parameters

        Example:
            >>> api.trainings.delete('training-id-123')
        """
        ...

    def update(
        self,
        *,
        training: Training | PrimaryKey,
        event_time: datetime = ...,
        sim_start_time: datetime = ...,
        sim_end_time: datetime = ...,
        **kwargs: Any,
    ) -> Training:
        # fmt: off
        """Update individual fields of a training event.

        Only event_time, sim_start_time, and sim_end_time can be updated.
        Name, parent simulation, checkpoint, and attendees cannot be modified
        after creation.

        Timing Constraints:
            - event_time: Must be at least 5h in the future
            - sim_start_time: Must be 1h+ in future and 4h before event_time
            - sim_end_time: Must be at least 24h after event_time

        Args:
            training: Training instance or training ID
            event_time: When the training event will occur
            sim_start_time: When workbenches are created/started
            sim_end_time: When workbenches expire/destroyed
            **kwargs: Additional fields for future API compatibility

        Returns:
            Updated Training instance

        Raises:
            ValidationError: If timing constraints are violated

        Example:
            >>> training = api.trainings.get('training-id-123')
            >>> api.trainings.update(
            ...     training=training,
            ...     event_time=datetime(2026, 3, 15, 9, 0),
            ...     sim_start_time=datetime(2026, 3, 15, 5, 0)
            ... )
        """
        ...
        # fmt: on
    def add_attendees(
        self,
        *,
        training: Training | PrimaryKey,
        attendees: builtins.list[str],
        **kwargs: Any,
    ) -> None:
        # fmt: off
        """Add attendees to an existing training event.

        Args:
            training: Training instance or training ID
            attendees: List of email addresses to add
            **kwargs: Additional parameters

        Example:
            >>> api.trainings.add_attendees(
            ...     training='training-id-123', attendees=['newuser@example.com']
            ... )
        """
        ...
        # fmt: on
    def remove_attendees(
        self,
        *,
        training: Training | PrimaryKey,
        attendees: builtins.list[str],
        **kwargs: Any,
    ) -> None:
        """Remove attendees from an existing training event.

        Args:
            training: Training instance or training ID
            attendees: List of email addresses to remove
            **kwargs: Additional parameters

        Example:
            >>> api.trainings.remove_attendees(  # fmt: skip
            ...     training='training-id-123', attendees=['user@example.com']
            ... )
        """
        ...

    def get_external_user_group(
        self, *, training: Training | PrimaryKey, **kwargs: Any
    ) -> TrainingNGCData:
        # fmt: off
        """Get NGC external user group data for a training.

        Makes an external API call to NGC to retrieve full details about the
        training's user group, including confirmed users and pending invitations.

        Requires AIR_INSTRUCTOR, AIR_ORG_ADMIN, or USER_ADMIN roles.

        Args:
            training: Training instance or ID
            **kwargs: Additional parameters

        Returns:
            NGC user group data including members and invitation status

        Example:
            >>> group_data = api.trainings.get_external_user_group(
            ...     training='training-id-123'
            ... )
            >>> print(f"Group name: {group_data['name']}")
            >>> print(f"Organization: {group_data['orgName']}")
            >>> confirmed = group_data.get('confirmedUsers', [])
            >>> pending = group_data.get('pendingInvitations', [])
            >>> print(f"Total users: {len(confirmed)} confirmed, {len(pending)} pending")
        """
        ...
        # fmt: on
