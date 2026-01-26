# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: MIT

"""
Decorators for backward compatibility layer.
"""

import warnings
from functools import wraps
from typing import Any, Callable, TypeVar, cast

F = TypeVar('F', bound=Callable[..., Any])


def deprecated(message: str) -> Callable[[F], F]:
    """Decorator to mark methods as deprecated with a custom warning message.

    Args:
        message: The deprecation message to display to users

    Returns:
        Decorated function that emits a DeprecationWarning when called

    Example:
        @deprecated("Use new_method() instead")
        def old_method(self):
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
