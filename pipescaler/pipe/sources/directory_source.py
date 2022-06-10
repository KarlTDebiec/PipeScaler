#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a directory."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Collection, Sequence, Union

from pipescaler.common import validate_input_directory
from pipescaler.core import PipeImage, basic_sort, get_files
from pipescaler.core.pipe import Source


class DirectorySource(Source):
    """Yields images from a directory."""

    exclusions = {".DS_Store", "desktop"}
    """Base filenames to exclude"""

    def __init__(
        self,
        directory: Union[Union[Path, str], Sequence[Union[Path, str]]],
        exclusions: Union[str, Collection[str]] = None,
        sort: Callable[[str], int] = basic_sort,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory from which to yield files
            exclusions: Base filenames to exclude
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        if exclusions is None:
            exclusions = set()
        exclusions |= self.exclusions

        # Store configuration
        if isinstance(directory, str) or isinstance(directory, Path):
            directory = [directory]
        self.directories = [Path(validate_input_directory(d)) for d in directory]
        self.sort = sort

        # Store list of filenames
        filenames = get_files(self.directories, style="absolute", exclusions=exclusions)
        filenames = list(filenames)
        filenames.sort(key=self.sort, reverse=True)
        self.filenames = filenames
        self.index = 0

    def __next__(self):
        if self.index < len(self.filenames):
            filename = self.filenames[self.index]
            self.index += 1
            return PipeImage(path=filename)
        raise StopIteration
