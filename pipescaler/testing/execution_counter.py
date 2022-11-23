#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Decorator to count the number of times a function is executed."""
from __future__ import annotations

from typing import Callable, Generic, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


class ExecutionCounter(Generic[P, R]):
    """Counts the number of times a function is called."""

    count: int

    def __init__(self, function: Callable[P, R]) -> None:
        """Initializes.

        Arguments:
            function: Function whose execution to count
        """
        self.count = 0
        """Number of times the function has been called"""
        self.function = function
        """Function whose executions to count"""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Calls the function and increments the counter.

        Arguments:
            args: Positional arguments
            kwargs: Keyword arguments
        Returns:
            Result of the function
        """
        self.count += 1
        return self.function(*args, **kwargs)


def count_executions(function: Callable[P, R]) -> ExecutionCounter[P, R]:
    """Decorator to count the number of times a function is executed.

    Arguments:
        function: Function to decorate
    Returns:
        Decorated function
    """
    return ExecutionCounter(function)
