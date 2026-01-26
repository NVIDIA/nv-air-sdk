# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Stub file for ssh_keys endpoint type hints.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey

@dataclass(eq=False)
class SSHKey(AirModel):
    """SSH Key model representing a user's SSH public key.

    The string representation shows: id, name

    Attributes:
        id: Unique identifier for the SSH key
        created: Timestamp when the SSH key was created
        name: Human-readable name for the SSH key
        fingerprint: SSH key fingerprint (automatically generated)
    """

    id: str
    created: datetime
    name: str
    fingerprint: str

    @classmethod
    def get_model_api(cls) -> type[SSHKeyEndpointAPI]: ...
    @property
    def model_api(self) -> SSHKeyEndpointAPI: ...
    def delete(self) -> None:
        """Delete this SSH key.

        After deletion, the instance's id will be set to None.

        Example:
            >>> ssh_key = api.ssh_keys.get('key-id')
            >>> ssh_key.delete()
        """
        ...

class SSHKeyEndpointAPI(BaseEndpointAPI[SSHKey]):
    """API client for SSH key endpoints."""

    API_PATH: str
    model: type[SSHKey]

    def list(  # type: ignore[override]
        self,
        *,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
    ) -> Iterator[SSHKey]:
        """List all SSH keys with optional filtering.

        Args:
            limit: Maximum number of results to return per page
            offset: The initial index from which to return the results
            ordering: Order objects by field. Prefix with "-" for desc order
            search: Search by name

        Returns:
            Iterator of SSHKey instances

        Example:
            >>> # List all SSH keys
            >>> for key in api.ssh_keys.list():
            ...     print(key.name, key.fingerprint)

            >>> # Search by name
            >>> for key in api.ssh_keys.list(search='my-key'):
            ...     print(key.name)

            >>> # Order by name descending
            >>> for key in api.ssh_keys.list(ordering='-name'):
            ...     print(key.name)
        """
        ...

    def create(self, *, name: str, public_key: str) -> SSHKey:
        """Create a new SSH key.

        Args:
            name: Human-readable name for the SSH key
            public_key: The SSH public key content (e.g., "ssh-rsa AAAA...")

        Returns:
            The created SSHKey instance

        Example:
            >>> ssh_key = api.ssh_keys.create(
            name='my-laptop-key', public_key='ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB...'
            )
            >>> print(ssh_key.fingerprint)
        """
        ...

    def get(self, pk: PrimaryKey) -> SSHKey:
        """Get a specific SSH key by ID.

        Args:
            pk: The SSH key ID (string or UUID)

        Returns:
            The SSHKey instance

        Example:
            >>> ssh_key = api.ssh_keys.get('key-id')
            >>> print(ssh_key.name, ssh_key.fingerprint)
        """
        ...

    def delete(self, pk: PrimaryKey) -> None:
        """Delete an SSH key by ID.

        Args:
            pk: The SSH key ID (string or UUID)

        Returns:
            None

        Example:
            >>> # Delete by ID
            >>> api.ssh_keys.delete('key-id')

        """
        ...
