#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a directory."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional, Sequence, Union

from pipescaler.common import validate_input_directories
from pipescaler.core.pipelines import PipeImage, Source
from pipescaler.core.sorting import basic_sort


class HierarchicalDirectorySource(Source):
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

        # Store list of file_paths
        file_paths = []
        for directory in self.directories:
            file_paths.extend(self.scandir(directory))
        file_paths.sort(
            key=lambda file_path: self.sort(file_path), reverse=self.reverse
        )
        self.file_paths = file_paths
        self.index = 0

    def scandir(self, directory: Path) -> list[Path]:
        """Yield next image."""
        file_paths = []
        for file_path in [f for f in directory.iterdir() if f.is_file()]:
            if file_path.stem not in self.exclusions:
                file_paths.append(file_path)
        for subdirectory_path in [d for d in directory.iterdir() if d.is_dir()]:
            file_paths.extend(self.scandir(subdirectory_path))

        return file_paths

    def __next__(self):
        """Yield next image."""
        if self.index < len(self.file_paths):
            file_path = self.file_paths[self.index]
            self.index += 1
            return PipeImage(path=file_path)
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
