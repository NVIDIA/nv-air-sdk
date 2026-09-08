# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI, PrimaryKey

class PlatformInformationPortMapEntry(TypedDict):
    """A single port map entry.

    Attributes:
        asic: The ASIC this entry applies to
        label_port: The label port for the given ASIC
        local_port: The local port for the given ASIC
        split_num: The split number for the given ASIC
    """

    asic: str
    label_port: str
    local_port: str
    split_num: str

#: Port map layout: split factor (`'1'`, `'2'`, ... or `'mgmt'`) -> label port
#: -> entry. Both outer levels have open-ended keys, so they stay plain dicts
#: rather than TypedDicts.
PlatformInformationPortMap = dict[str, dict[str, PlatformInformationPortMapEntry]]

class MinimumResources(TypedDict):
    """Minimum resources required to run a platform.

    Attributes:
        cpu: Number of CPU cores
        memory: Memory, in MiB
        storage: Storage, in GiB
    """

    cpu: int
    memory: int
    storage: int

class PortsConfig(TypedDict):
    """Label port count and split configuration for a platform.

    Attributes:
        num_label_ports: Number of label ports on the platform
        default_split: Default split factor applied to each label port
                       (`'1'` = un-split)
        split_options: Permitted split factors
    """

    num_label_ports: int
    default_split: str
    split_options: list[str]

@dataclass(eq=False)
class PlatformInformation(AirModel):
    """Hardware platform characteristics for one model.

    Describes the ports, resources and simulator configuration for a single
    hardware model. An `OSImageManifest` pins a specific platform information
    version per model.

    Exactly one of `os_type` or `emulation_type` must be non-empty. The API
    enforces this; supplying both or neither returns a 400. The unset one is
    returned as `None`.

    Note:
        Every entry in `ports_config['split_options']`, and
        `ports_config['default_split']`, must appear as a key in `port_map`
        (the `'mgmt'` bucket excepted). The API enforces this; a mismatch
        returns a 400.

    Attributes:
        id: Unique identifier for the platform information record
        created: Timestamp when the record was created
        modified: Timestamp when the record was last modified
        model: Hardware model name, e.g. `SN3700`
        platform_information_version: Version of this record, referenced by
                                      the `platforms` pins on an
                                      `OSImageManifest`
        port_map: Split factor to label port to port map entry
        ports_config: Label port count and split configuration
        creator: Email of the user who created the record
        os_type: The OS type this platform runs. Mutually exclusive with
                 `emulation_type`; `None` when unset
        emulation_type: The emulation type for this platform. Mutually
                        exclusive with `os_type`; `None` when unset
        vars: Free-form key-value variables. Empty when unset
        simulator_config: Free-form simulator configuration. Empty when unset
        minimum_resources: Minimum CPU, memory and storage to run the
                           platform. `None` when the API sets no minimum
    """

    id: str
    created: datetime
    modified: datetime
    model: str
    platform_information_version: str
    port_map: PlatformInformationPortMap
    ports_config: PortsConfig
    creator: str | None
    os_type: str | None
    emulation_type: str | None
    vars: dict[str, Any]
    simulator_config: dict[str, Any]
    minimum_resources: MinimumResources | None

    @classmethod
    def get_model_api(cls) -> type[PlatformInformationEndpointAPI]: ...
    @property
    def model_api(self) -> PlatformInformationEndpointAPI: ...
    def delete(self) -> None:
        """Delete this platform information record.

        Returns:
            None

        Example:
            >>> platform.delete()
        """
        ...

class PlatformInformationEndpointAPI(BaseEndpointAPI[PlatformInformation]):
    """Endpoint API for managing platform information.

    Provides listing, retrieval, creation, and deletion of the records
    describing hardware platform characteristics. The API does not support
    partial or full updates on this resource.
    """

    API_PATH: str
    model: type[PlatformInformation]

    def list(
        self,
        *,
        creator: str = ...,
        emulation_type: str = ...,
        model: str = ...,
        os_type: str = ...,
        platform_information_version: str = ...,
        limit: int = ...,
        offset: int = ...,
        ordering: str = ...,
        search: str = ...,
        **kwargs: Any,
    ) -> Iterator[PlatformInformation]:
        # fmt: off
        """List platform information records.

        Args:
            creator: Filter by creator email
            emulation_type: Filter by emulation type
            model: Filter by hardware model name
            os_type: Filter by OS type
            platform_information_version: Filter by version
            limit: Number of results to return per page
            offset: Initial index from which to return results
            ordering: Order by field (prefix with "-" for descending)
            search: Search across platform information fields
            **kwargs: Additional filter parameters

        Returns:
            Iterator of PlatformInformation instances

        Example:
            >>> for platform in api.platform_information.list(model='SN3700'):
            ...     print(platform.platform_information_version)
        """
        ...
        # fmt: on
    def get(self, pk: PrimaryKey, **kwargs: Any) -> PlatformInformation:
        """Retrieve a specific platform information record.

        Args:
            pk: Platform information UUID
            **kwargs: Additional query parameters

        Returns:
            PlatformInformation instance

        Example:
            >>> platform = api.platform_information.get('platform-uuid')
            >>> print(platform.model, platform.ports_config)
        """
        ...

    def create(
        self,
        *,
        model: str,
        platform_information_version: str,
        port_map: PlatformInformationPortMap,
        ports_config: PortsConfig,
        os_type: str = ...,
        emulation_type: str = ...,
        vars: dict[str, Any] = ...,
        simulator_config: dict[str, Any] = ...,
        minimum_resources: MinimumResources = ...,
        **kwargs: Any,
    ) -> PlatformInformation:
        """Create a platform information record.

        Exactly one of `os_type` or `emulation_type` must be supplied.

        Args:
            model: Hardware model name, e.g. `SN3700`
            platform_information_version: Version of this record
            port_map: Split factor (`'1'`, `'2'`, ... or `'mgmt'`) to label
                      port to port map entry
            ports_config: Label port count and split configuration
            os_type: The OS type this platform runs. Mutually exclusive with
                     `emulation_type`
            emulation_type: The emulation type. Mutually exclusive with
                            `os_type`
            vars: Free-form key-value variables
            simulator_config: Free-form simulator configuration
            minimum_resources: Minimum CPU, memory and storage
            **kwargs: Additional fields for future API compatibility

        Returns:
            The created PlatformInformation instance

        Example:
            >>> platform = api.platform_information.create(
            ...     model='SN3700',
            ...     platform_information_version='1.2',
            ...     os_type='cumulus-linux',
            ...     port_map={
            ...         '1': {
            ...             'swp1': {
            ...                 'asic': '1',
            ...                 'label_port': '1',
            ...                 'local_port': '1',
            ...                 'split_num': '1',
            ...             }
            ...         },
            ...         '2': {
            ...             'swp1s0': {
            ...                 'asic': '1',
            ...                 'label_port': '1',
            ...                 'local_port': '1',
            ...                 'split_num': '1',
            ...             },
            ...             'swp1s1': {
            ...                 'asic': '1',
            ...                 'label_port': '1',
            ...                 'local_port': '2',
            ...                 'split_num': '2',
            ...             },
            ...         },
            ...     },
            ...     ports_config={
            ...         'num_label_ports': 1,
            ...         'default_split': '1',
            ...         'split_options': ['1', '2'],
            ...     },
            ...     minimum_resources={'cpu': 2, 'memory': 2048, 'storage': 10},
            ... )
        """
        ...

    def delete(self, pk: PrimaryKey, **kwargs: Any) -> None:
        """Delete a platform information record.

        Args:
            pk: Platform information UUID
            **kwargs: Additional parameters

        Returns:
            None

        Example:
            >>> api.platform_information.delete('platform-uuid')
        """
        ...
