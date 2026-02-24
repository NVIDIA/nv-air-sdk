# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Constants shared throughout the SDK.
"""

from datetime import timedelta
from enum import Enum
from urllib.parse import ParseResult, urlparse

DEFAULT_CONNECT_TIMEOUT = timedelta(seconds=16)
DEFAULT_READ_TIMEOUT = timedelta(seconds=61)
DEFAULT_PAGINATION_PAGE_SIZE = 200  # Objects per paginated response

# Request retry configuration
DEFAULT_RETRY_ATTEMPTS: int = 5
DEFAULT_RETRY_BACKOFF_FACTOR: float = 1.0
DEFAULT_RETRY_BACKOFF_JITTER: float = 1.0

# Image upload configuration
# Multipart upload chunk size (~100MB for balance of speed/reliability)
MULTIPART_CHUNK_SIZE = 100 * 1000 * 1000  # 100 MB in bytes
# Minimum part size for S3 multipart (5 MiB, except for last part)
MULTIPART_MIN_PART_SIZE = 5 * 1024 * 1024  # 5 MiB in bytes
# Maximum recommended concurrent workers for multipart uploads
MAX_RECOMMENDED_UPLOAD_WORKERS = 10
# Default timeout per part upload
DEFAULT_UPLOAD_TIMEOUT = timedelta(minutes=5)


class HTTPHeaders(str, Enum):
    """Known HTTP headers."""

    # Well-known headers
    CONTENT_TYPE = 'Content-Type'
    AUTHORIZATION = 'Authorization'
    USER_AGENT = 'User-Agent'

    # Air-specific headers
    AIR_SDK_SYS_VERSION = 'X-Air-Sdk-Sys-Version'
    AIR_SDK_VERSION = 'X-Air-Sdk-Version'
    AIR_SDK_TIMEZONE = 'X-Air-Sdk-Timezone'
    AIR_SDK_PLATFORM = 'X-Air-Sdk-Platform'


class TopologyFormat(str, Enum):
    """Topology format types."""

    JSON = 'JSON'
    DOT = 'DOT'


SCOPED_KEY_PREFIX = 'nvapi-'
AIR_API_URL = 'https://api.air-ngc.nvidia.com/'

NGC_API_PROD_URL = 'https://api.ngc.nvidia.com'
NGC_API_STG_URL = 'https://api.stg.ngc.nvidia.com'


def get_ngc_api_base_url(api_url: str) -> ParseResult:
    """Return the NGC API base URL based on the Air API URL.

    If the api_url contains 'stg', the staging NGC URL is used.
    Otherwise, the production NGC URL is used.
    """
    base = NGC_API_STG_URL if 'stg' in api_url else NGC_API_PROD_URL
    return urlparse(base)


def get_ngc_device_login_url(api_url: str) -> ParseResult:
    """Return the NGC device login URL."""
    return get_ngc_api_base_url(api_url)._replace(
        path='/device/login',
    )


def get_ngc_token_url(api_url: str) -> ParseResult:
    """Return the NGC token URL."""
    return get_ngc_api_base_url(api_url)._replace(
        path='/token',
    )


def get_ngc_sak_details_url(api_url: str) -> ParseResult:
    """Return the NGC SAK details URL."""
    return get_ngc_api_base_url(api_url)._replace(
        path='/v3/keys/get-caller-info',
    )


def get_ngc_me_url(api_url: str) -> ParseResult:
    """Return the NGC user info URL."""
    return get_ngc_api_base_url(api_url)._replace(
        path='/v2/users/me',
    )
