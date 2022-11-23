#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from typing import Callable, Generic, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


class PipeSplitterWithCheckpoints(Generic[P, R]):
    """Wraps a PipeSplitter to add checkpointing."""

    cpts: list[str]
    internal_cpts: list[str]

    def __init__(
        self, function: Callable[P, R], cpts: list[str], internal_cpts: list[str]
    ) -> None:
        """Initializes.

        Arguments:
            function: Function to wrap
            cpts: Names of checkpoints
            internal_cpts: Names of internal checkpoints
        """
        self.function = function
        """Function to wrap"""
        self.cpts = cpts
        """Names of checkpoints"""
        self.internal_cpts = internal_cpts
        """Names of checkpoints of functions called within the wrapped function"""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Calls the function."""
        return self.function(*args, **kwargs)
