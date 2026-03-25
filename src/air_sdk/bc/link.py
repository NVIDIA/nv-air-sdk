# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Links-specific backward compatibility layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from air_sdk.air_model import PrimaryKey
from air_sdk.bc.base import AirModelCompatMixin
from air_sdk.bc.decorators import deprecated
from air_sdk.bc.utils import drop_removed_fields, map_field_names
from air_sdk.utils import validate_payload_types

if TYPE_CHECKING:
    from air_sdk.endpoints.links import Link
    from air_sdk.endpoints.simulations import Simulation


class LinkCompatMixin(AirModelCompatMixin):
    """Mixin providing Link-specific v1/v2 SDK backward compatibility.

    This maintains compatibility with link fields and methods from older SDK versions.
    """

    _REMOVED_FIELDS = [
        'topology',
        'ids',
    ]
    _FIELD_MAPPINGS: dict[str, str] = {}

    def update(self, **kwargs: Any) -> Any:
        raise NotImplementedError(
            'The `update()` method is not supported in the current air-api version.'
        )


class LinkEndpointAPICompatMixin:
    """Mixin providing API-level backward compatibility for Link endpoints.

    This handles BC for API-level methods (create, list, etc.)
    where future versions may need different parameters or transformations.
    """

    def create(self, *args: Any, **kwargs: Any) -> Link:
        """Create a link with v1/v2 backward compatibility.

        Handles:
        - Field name mapping (see LinkCompatMixin._FIELD_MAPPINGS)
        - Removed fields (see LinkCompatMixin._REMOVED_FIELDS)
        """
        drop_removed_fields(kwargs, LinkCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, LinkCompatMixin._FIELD_MAPPINGS)
        return super().create(*args, **kwargs)  # type: ignore[no-any-return, misc]

    def list(self, *args: Any, **kwargs: Any) -> Any:
        """List links with v1/v2 filter name compatibility.

        Handles:
        - Field name mapping (see LinkCompatMixin._FIELD_MAPPINGS)
        - Removed filters (see LinkCompatMixin._REMOVED_FIELDS)
        """
        drop_removed_fields(kwargs, LinkCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, LinkCompatMixin._FIELD_MAPPINGS)
        return super().list(*args, **kwargs)  # type: ignore[misc]

    @validate_payload_types
    @deprecated('bulk_create() is deprecated, use create() for each link instead.')
    def bulk_create(
        self,
        links: list[dict[str, Any]],  # type: ignore[valid-type]
        **kwargs: Any,
    ) -> list[Link]:  # type: ignore[valid-type]
        """Bulk create links with v1/v2 backward compatibility.

        The bulk-create API endpoint no longer exists. This method now
        creates links one at a time by calling create() for each link.

        Args:
            links: List of link dictionaries with format
                ``{"simulation_interfaces": [i1, i2]}`` (v1/v2)
                or ``{"interfaces": [i1, i2]}`` (v3).
            **kwargs: Additional keyword arguments forwarded to
                :meth:`create`, e.g. ``simulation``.

        Returns:
            List of created Link objects.

        Raises:
            ValueError: If the link dictionaries are missing both
                ``simulation_interfaces`` and ``interfaces`` keys.

        .. deprecated::
            Use :meth:`create` for each link instead.
        """
        # Drop any removed fields that might have been passed
        drop_removed_fields(kwargs, LinkCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, LinkCompatMixin._FIELD_MAPPINGS)

        # Create links one by one, with rollback on failure
        created_links = []

        try:
            for link in links:  # type: ignore[attr-defined]
                # Extract interfaces from the link dictionary
                # Support both v1/v2 'simulation_interfaces' and v3 'interfaces'
                if 'simulation_interfaces' in link:
                    interfaces = link['simulation_interfaces']
                elif 'interfaces' in link:
                    interfaces = link['interfaces']
                else:
                    raise ValueError(
                        f'Expected format '
                        f'{{"simulation_interfaces": [interface_1, interface_2]}} '
                        f'or {{"interfaces": [interface_1, interface_2]}} '
                        f'but got {link}'
                    )

                # Create the link, forwarding kwargs (e.g. simulation) so the
                # API can validate them. create() handles its own BC cleanup.
                created_link = self.create(interfaces=interfaces, **kwargs)
                created_links.append(created_link)

        except Exception:
            # Rollback: Delete all links created in this request
            # (to match the old API behavior)
            for link in created_links:
                try:
                    self.delete(link.id)  # type: ignore[attr-defined]
                except Exception:
                    # Ignore errors during rollback cleanup
                    pass
            # Re-raise the original error from API or validation
            raise

        return created_links

    @deprecated('bulk_delete() is deprecated, use delete() for each link instead.')
    @validate_payload_types
    def bulk_delete(
        self, simulation: Simulation | PrimaryKey, **kwargs: Any
    ) -> dict[str, int]:
        """Bulk delete links with v1/v2 backward compatibility.

        The bulk-delete API endpoint no longer exists. This method now deletes
        links one at a time by calling delete() for each link.

        Old format:
            bulk_delete(simulation=sim, links=[link1, link2, ...])
            bulk_delete(simulation=sim)  # Deletes all links in simulation

        Args:
            simulation: The simulation to delete links from
            links: Optional list of Link objects or IDs to delete.
                  If None, deletes all links.

        Returns:
            Dictionary with count of deleted links: {'links_deleted': N}
            Note: Invalid or already-deleted IDs are silently skipped
                 (matching old API behavior)

        Raises:
            ValueError: If simulation is not provided or links is an empty list
        """
        # Drop any removed fields that might have been passed
        drop_removed_fields(kwargs, LinkCompatMixin._REMOVED_FIELDS)
        map_field_names(kwargs, LinkCompatMixin._FIELD_MAPPINGS)

        # Get links to delete
        links = kwargs.get('links')

        if links is not None and not isinstance(links, list):
            raise ValueError('`links` must be a list.')

        # Validate links if provided
        if isinstance(links, list) and len(links) == 0:
            raise ValueError('If `links` is provided it must be a non-empty list.')

        # Determine which links to delete
        if links:
            links_to_delete = links
        else:
            # If no links provided, get all links in the simulation
            links_to_delete = list(self.list(simulation=simulation))

        # Delete each link, silently skip failures (matching old API behavior)
        deleted_count = 0
        for link in links_to_delete:
            # Extract link ID (handle both Link objects and string IDs)
            link_id = link.id if hasattr(link, 'id') else str(link)

            try:
                self.delete(link_id)  # type: ignore[attr-defined]
                deleted_count += 1
            except Exception:
                # Silently skip failed deletions (e.g., invalid IDs, already deleted)
                # This matches the old API behavior which didn't fail on invalid IDs
                pass

        return {'links_deleted': deleted_count}
