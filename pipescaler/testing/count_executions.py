#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Decorator to count the number of times a function is called."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def count_executions(function: Callable) -> Callable:
    """Decorator to count the number of times a function is called.

    Arguments:
        function: Function to wrap
    Returns:
        Wrapped function
    """

    @wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        """Wrapped function.

        Arguments:
            *args: Positional arguments
            **kwargs: Keyword arguments
        Returns:
            Result of wrapped function
        """
        wrapped.count += 1
        return function(*args, **kwargs)

    wrapped.count = 0
    return wrapped
