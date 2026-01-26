# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import configparser
import os
import platform
import sys
import webbrowser
from datetime import datetime as dt
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

import air_sdk
from air_sdk import const, exceptions, utils


class Client(requests.Session):
    """A session client for managing the execution of API requests."""

    def __init__(self, api_url: str):
        super().__init__()
        self.headers.update({'content-type': 'application/json', 'Authorization': ''})
        self.api_url = utils.normalize_api_url(api_url)
        self.connect_timeout = const.DEFAULT_CONNECT_TIMEOUT
        self.read_timeout = const.DEFAULT_READ_TIMEOUT
        self.pagination_page_size = const.DEFAULT_PAGINATION_PAGE_SIZE

        # Set session headers
        self.headers.update(self.get_basic_headers())
        self.headers.update(self.get_telemetry_headers())

        # Set HTTP adapter for all requests
        adapter = self.get_http_adapter()
        self.mount('https://', adapter)
        self.mount('http://', adapter)

    def get_basic_headers(self) -> dict[str, str]:
        """Return generic headers for all requests."""
        return {
            const.HTTPHeaders.CONTENT_TYPE: 'application/json',
            const.HTTPHeaders.AUTHORIZATION: '',
            const.HTTPHeaders.USER_AGENT: self.get_user_agent_header_value(),
        }

    @staticmethod
    def get_telemetry_headers() -> dict[str, str]:
        """Return telemetry-specific headers for all requests."""
        tz_name = dt.now().astimezone().tzname() or 'Unknown'
        return {
            const.HTTPHeaders.AIR_SDK_SYS_VERSION: sys.version,
            const.HTTPHeaders.AIR_SDK_VERSION: air_sdk.__version__,
            const.HTTPHeaders.AIR_SDK_TIMEZONE: tz_name,
            const.HTTPHeaders.AIR_SDK_PLATFORM: platform.platform(),
        }

    def get_user_agent_header_value(self) -> str:
        """Return the user agent header value."""
        return f'air-sdk/{air_sdk.__version__}'

    def get_http_adapter(self) -> HTTPAdapter:
        """Return an HTTP adapter for all requests."""
        return HTTPAdapter(max_retries=self.get_retry_strategy())

    def get_retry_strategy(self) -> Retry:
        """
        Return a retry strategy for all requests.
        The following retry strategy will attempt to retry the request
        only if the connection fails.
        """
        return Retry(
            total=const.DEFAULT_RETRY_ATTEMPTS,
            backoff_factor=const.DEFAULT_RETRY_BACKOFF_FACTOR,
            backoff_jitter=const.DEFAULT_RETRY_BACKOFF_JITTER,
        )

    def hunt_for_sak(self) -> str:
        config_path = os.path.expanduser('~/.ngc/config')
        if not os.path.exists(config_path):
            raise exceptions.AirError(
                'No ~/.ngc/config file found. Please run `ngc config set` to set SAK '
                'or use AirApi.with_api_key(api_key=<YOUR_STARFLEET_API_KEY>) directly'
            )

        config = configparser.ConfigParser()

        # `ngc config set` uses semicolons for comments - ignore these
        with open(config_path, encoding='utf-8') as fh:
            config.read_file(filter(lambda line: not line.strip().startswith(';'), fh))

        # Find all profiles with API keys
        profiles_with_keys = []
        for section in config.sections():
            if 'apikey' in config[section]:
                profiles_with_keys.append((section, config[section]['apikey']))

        # Handle different cases
        if not profiles_with_keys:
            raise exceptions.AirError('No API keys found in ~/.ngc/config')
        elif len(profiles_with_keys) == 1:
            return profiles_with_keys[0][1]
        else:
            # Multiple profiles found, always throw an error
            profiles_list = ', '.join([f"'{p[0]}'" for p in profiles_with_keys])
            raise exceptions.AirError(
                f'Found API keys for multiple profiles: {profiles_list}. Please choose '
                'one API key by using AirApi.with_api_key(<YOUR_STARFLEET_API_KEY>)'
            )

    def ngc_sak_login(self) -> None:
        """
        Log in with Scoped API Key (SAK)

        No args. Client must have directory ~/.ngc/config
        """
        sak = self.hunt_for_sak()
        is_scoped_key = sak.startswith(const.SCOPED_KEY_PREFIX)

        if not is_scoped_key:
            raise exceptions.AirError('Non-scoped API keys are not yet supported by Air')

        self.headers.update(
            {
                # Use the SAK as the bearer token directly
                'Authorization': f'Bearer {sak}',
            }
        )

    def ngc_device_login(self, email: str, ngc_org_name: str) -> None:
        """Log in with device login - does not require a NGC API Key/SAK."""
        device_id = utils.create_short_uuid()

        # Get session key via device login
        device_login_data = {'deviceId': device_id, 'email': email}

        login_response = requests.post(
            const.NGC_DEVICE_LOGIN_URL.geturl(), json=device_login_data
        )

        if login_response.status_code != 200:
            raise exceptions.AirError(
                f'Request to get device login URL failed, '
                f'returned HTTP {login_response.status_code}'
            )

        login_data = login_response.json()
        login_url, session_key = login_data.get('loginUrl'), login_data.get('sessionKey')
        if not login_url or not session_key:
            raise exceptions.AirError('Failed to get login URL or session key from NGC')

        webbrowser.open(login_url)

        if not sys.stdin.isatty():
            raise exceptions.AirError(
                'Device login is not supported in non-interactive environments. '
                'Please use AirApi.with_api_key(api_key=<YOUR_STARFLEET_API_KEY>) '
                'instead.'
            )

        _ = input('Press Enter after completing authentication in browser...\n').strip(
            '\r'
        )

        # Use session key to get token
        token_url = const.NGC_TOKEN_URL
        token_headers = {
            'Authorization': f'Bearer {session_key}',
            'X-Device-Id': device_id,
        }

        token_response = requests.get(token_url.geturl(), headers=token_headers)

        if token_response.status_code != 200:
            raise exceptions.AirError(
                f'Error: Failed to get token for {email} in org {ngc_org_name}'
            )

        if token := token_response.json().get('token', None):
            self.headers.update(
                {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json',
                    'Nv-Ngc-Org': ngc_org_name,
                }
            )

        else:
            raise exceptions.AirError('Response returned 200 but token was not present')

    def request(self, *args: Any, **kwargs: Any) -> requests.Response:
        """Override request method to pass the timeout"""
        kwargs.setdefault(
            'timeout',
            (
                self.connect_timeout.total_seconds(),
                self.read_timeout.total_seconds(),
            ),
        )
        return super().request(*args, **kwargs)
