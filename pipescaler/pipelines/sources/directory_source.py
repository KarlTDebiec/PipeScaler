#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a directory."""
from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import Any, Callable, Optional, Sequence, Union

from pipescaler.common import validate_input_directories
from pipescaler.core.pipelines import PipeImage, Source
from pipescaler.core.sorting import basic_sort


class DirectorySource(Source):
    """Yields images from a directory."""

    cls_exclusions = {".DS_Store", "desktop"}
    """Base filenames to exclude"""

    def __init__(
        self,
        directory: Union[Union[Path, str], Sequence[Union[Path, str]]],
        exclusions: Optional[set[str]] = None,
        sort: Union[Callable[[str], int], Callable[[str], str]] = basic_sort,
        reverse: bool = False,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory or directories from which to yield files
            exclusions: Filenames stems to exclude
            sort: Function to sort filenames
            reverse: Whether to reverse sort order
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.directories = validate_input_directories(directory)
        self.exclusions = self.cls_exclusions
        if exclusions is not None:
            self.exclusions |= exclusions
        self.sort = sort
        self.reverse = reverse

        # Store list of filenames
        filenames = list(chain.from_iterable(d.iterdir() for d in self.directories))
        filenames = [f for f in filenames if f.stem not in self.exclusions]
        filenames.sort(
            key=lambda filename: self.sort(filename.stem), reverse=self.reverse
        )
        self.filenames = filenames
        self.index = 0

    def __next__(self):
        """Yield next image."""
        if self.index < len(self.filenames):
            filename = self.filenames[self.index]
            self.index += 1
            return PipeImage(path=filename)
        raise StopIteration

    def __repr__(self):
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"directory={self.directories}, "
            f"exclusions={self.exclusions}"
            f"sort={self.sort},"
            f"reverse={self.reverse})"
        )
