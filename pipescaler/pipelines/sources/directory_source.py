#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a directory."""
from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import Any, Callable, Optional, Sequence, Union

from pipescaler.common import validate_input_directory
from pipescaler.core.pipelines import PipeImage, Source
from pipescaler.core.sorting import basic_sort


class DirectorySource(Source):
    """Yields images from a directory."""

    exclusions = {".DS_Store", "desktop"}
    """Base filenames to exclude"""

    def __init__(
        self,
        directory: Union[Union[Path, str], Sequence[Union[Path, str]]],
        exclusions: Optional[set[str]] = None,
        sort: Union[Callable[[str], int], Callable[[str], str]] = basic_sort,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            directory: Directory or directories from which to yield files
            exclusions: Filename stems to exclude
            sort: Function with which to sort filenames
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        if exclusions is None:
            exclusions = set()
        exclusions |= self.exclusions

        # Store configuration
        if isinstance(directory, (Path, str)):
            directory = [directory]
        self.directories = [Path(validate_input_directory(d)) for d in directory]
        self.sort = sort

        # Store list of filenames
        filenames = list(chain.from_iterable(d.iterdir() for d in self.directories))
        filenames = [f for f in filenames if f.stem not in self.exclusions]
        filenames.sort(key=lambda filename: self.sort(filename.stem))
        self.filenames = filenames
        self.index = 0

    def __next__(self):
        """Get next image from directories."""
        if self.index < len(self.filenames):
            filename = self.filenames[self.index]
            self.index += 1
            return PipeImage(path=filename)
        raise StopIteration
