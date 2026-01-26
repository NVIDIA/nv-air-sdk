# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
SDK-specific exceptions
"""

from typing import Optional


class AirError(Exception):
    def __init__(
        self,
        message: str = 'An error occurred within the air_sdk.AirApi',
        status_code: Optional[int] = None,
    ):
        self.status_code = status_code
        super().__init__(message)


class AirModelAttributeError(AirError):
    def __init__(
        self,
        message: str = 'An error occurred while accessing an AirModel attribute.',
        status_code: Optional[int] = None,
    ):
        self.message = message
        super().__init__(message=self.message, status_code=status_code)


class AirUnexpectedResponse(AirError):
    """Raised when the API returns an unexpected response."""

    def __init__(self, message: str = '', status_code: Optional[int] = None) -> None:
        self.message = 'Received an unexpected response from the Air API'
        if status_code:
            self.message += f' ({status_code})'
        self.message += f': {message}'
        super().__init__(message=self.message, status_code=status_code)


class AirForbiddenError(AirError):
    """Raised when an API call returns a 403 Forbidden error"""

    def __init__(
        self, message: str = 'Received 403 Forbidden. Please call AirApi.authorize().'
    ) -> None:
        self.message = message
        super().__init__(message=self.message, status_code=403)


class AirObjectDeleted(AirError):
    """Raised when accessing a previously instantiated object that was deleted."""

    def __init__(self, cls: type, message: str = '') -> None:
        self.message = message
        if not self.message:
            self.message = (
                f'{cls} object has been deleted and should no longer be referenced'
            )
        super().__init__(message=self.message)
