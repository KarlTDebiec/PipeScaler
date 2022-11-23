#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Types and classes for typing Pipeline elements."""
from typing import Callable, Generic, TypeVar

from typing_extensions import ParamSpec

from pipescaler.core.pipelines.pipe_image import PipeImage

PipeMerger = Callable[[PipeImage], PipeImage]
"""Merges two or more PipeImages into a single downstream PipeImage.

Note that this type is identical to PipeProcessor, because in Python f(x) and f(*x) use
the same type annotations.
"""
PipeProcessor = Callable[[PipeImage], PipeImage]
"""Processes a PipeImage, yielding a modified PipeImage."""
PipeSplitter = Callable[[PipeImage], tuple[PipeImage, ...]]
"""Splits one PipeImage into two or more downstream PipeImages."""

P = ParamSpec("P")
R = TypeVar("R")


class PipeProcessorWithCheckpoints(Generic[P, R]):
    """Wraps a PipeProcessor to add checkpointing."""

    cpt: str
    internal_cpts: list[str]

    def __init__(
        self, function: Callable[P, R], cpt: str, internal_cpts: list[str]
    ) -> None:
        """Initializes.

        Arguments:
            function: Function to wrap
            cpt: Name of checkpoint
            internal_cpts: Names of internal checkpoints
        """
        self.function = function
        """Function to wrap"""
        self.cpt = cpt
        """Name of checkpoint"""
        self.internal_cpts = internal_cpts
        """Names of checkpoints of functions called within the wrapped function"""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Calls the function."""
        return self.function(*args, **kwargs)


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
