# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""Sphinx configuration for NVIDIA Air SDK documentation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import air_sdk

# -- Project information -----------------------------------------------------
project = 'NVIDIA Air SDK'
copyright = '2026, NVIDIA CORPORATION & AFFILIATES'
author = 'Air Team'
version = release = air_sdk.__version__

# -- General configuration ---------------------------------------------------
extensions = [
    'autoapi.extension',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'nbsphinx',
]

# -- AutoAPI -----------------------------------------------------------------
autoapi_type = 'python'
autoapi_dirs = ['../../src/air_sdk']
autoapi_file_patterns = ['*.pyi', '*.py']
autoapi_root = 'api'
autoapi_ignore = [
    '**/bc/*',
    '**/v2/*',
    '**/air_model.py',
    '**/air_json_encoder.py',
    '**/client.py',
    '**/utils.py',
    '**/helpers/*',
    '**/mixins.py',
]


def _skip_index_page_members(_app, what, name, _obj, skip, _options):
    """Only show docstrings and submodule links on package index pages."""
    if what in ('module', 'package'):
        return skip
    if name.startswith('air_sdk.') and name.count('.') == 1:
        return True
    if name.startswith('air_sdk.endpoints.') and name.count('.') == 2:
        return True
    return skip


def setup(sphinx):
    sphinx.connect('autoapi-skip-member', _skip_index_page_members)


# -- Napoleon ----------------------------------------------------------------
napoleon_include_init_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True

# -- Intersphinx -------------------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}

# -- nbsphinx ----------------------------------------------------------------
nbsphinx_execute = 'never'

# -- HTML output -------------------------------------------------------------
html_theme = 'nvidia_sphinx_theme'
