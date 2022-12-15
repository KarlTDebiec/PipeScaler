#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a directory."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Optional, Union

from pipescaler.common import validate_input_directory
from pipescaler.core.pipelines import PipeImage, Source
from pipescaler.core.sorting import basic_sort


class HierarchicalDirectorySource(Source):
    """Yields images from a directory."""

    cls_exclusions = {r".*\.DS_Store$", r".*Thumbs.db$", r".*desktop$"}
    """File paths to exclude"""

    def __init__(
        self,
        directory: Union[Path, str],
        exclusions: Optional[set[str]] = None,
        sort: Union[Callable[[str], int], Callable[[str], str]] = basic_sort,
        reverse: bool = False,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory from which to yield files
            exclusions: File path to exclude
            sort: Function to sort filenames
            reverse: Whether to reverse sort order
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.directory = validate_input_directory(directory)
        if exclusions is None:
            exclusions = set()
        exclusions |= self.cls_exclusions
        self.exclusions = set()
        for exclusion in exclusions:
            if isinstance(exclusion, str):
                exclusion = re.compile(exclusion)
            elif not isinstance(exclusion, re.Pattern):
                raise TypeError(
                    f"Exclusion must be str or re.Pattern, not {type(exclusion)}"
                )
            self.exclusions.add(exclusion)
        self.sort = sort
        self.reverse = reverse

        # Store list of file_paths
        file_paths = self.scandir(self.directory, self.directory)
        file_paths.sort(
            key=lambda file_path: self.sort(str(file_path.relative_to(self.directory))),
            reverse=self.reverse,
        )
        self.file_paths = file_paths
        self.index = 0

    def scandir(self, root_directory: Path, directory: Path) -> list[Path]:
        """Yield next image."""
        file_paths = []
        for file_path in [f for f in directory.iterdir() if f.is_file()]:
            relative_path = file_path.relative_to(root_directory)
            if any(er.match(str(relative_path)) for er in self.exclusions):
                continue
            file_paths.append(file_path)
        for subdirectory_path in [d for d in directory.iterdir() if d.is_dir()]:
            file_paths.extend(self.scandir(root_directory, subdirectory_path))

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
