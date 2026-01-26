# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Constants shared throughout the SDK.
"""

from datetime import timedelta
from enum import Enum
from urllib.parse import urlparse

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


SCOPED_KEY_PREFIX = 'nvapi-stg-'
# TODO: change to production URL
AIR_API_URL = 'https://api.air.nvidia.com/api/'

NGC_API_BASE_URL = urlparse(
    'https://api.stg.ngc.nvidia.com'
)  # Will drop the stg eventually
NGC_DEVICE_LOGIN_URL = NGC_API_BASE_URL._replace(path='/device/login')
NGC_TOKEN_URL = NGC_API_BASE_URL._replace(path='/token')
NGC_SAK_DETAILS_URL = NGC_API_BASE_URL._replace(path='/v3/keys/get-caller-info')
NGC_ME_URL = NGC_API_BASE_URL._replace(path='/v2/users/me')
