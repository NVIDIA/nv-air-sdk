# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Compatibility shim for the pre-rename module path.

The plugin image manifest resource lived here as `Manifest` up to and including
1.6.1. It now lives in `plugin_image_manifests` as `PluginImageManifest`. This
module keeps `air_sdk.endpoints.manifests` importable for code written against
the older releases, and can be dropped in the next major version.

It belongs to the compatibility layer described in `bc/README.md` and is
excluded from the API reference for the same reason `bc/` is, but the file has
to sit here: the import path is the whole point of it.
"""

from air_sdk.endpoints.plugin_image_manifests import (
    PluginImageManifest,
    PluginImageManifestEndpointAPI,
)

__all__ = [
    'Manifest',  # pre-1.7 name for PluginImageManifest
    'ManifestEndpointAPI',  # pre-1.7 name for PluginImageManifestEndpointAPI
    'PluginImageManifest',
    'PluginImageManifestEndpointAPI',
]

Manifest = PluginImageManifest
ManifestEndpointAPI = PluginImageManifestEndpointAPI
