#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a directory."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Optional, Union

from pipescaler.common import PathLike, validate_input_directory
from pipescaler.core.pipelines import PipeImage, Source
from pipescaler.core.sorting import basic_sort


class DirectorySource(Source):
    """Yields images from a directory."""

    cls_exclusions = {r".*\.DS_Store$", r".*Thumbs.db$", r".*desktop$"}
    """File paths to exclude"""

    def __init__(
        self,
        directory: PathLike,
        *,
        exclusions: Optional[set[Union[str, re.Pattern]]] = None,
        inclusions: Optional[set[Union[str, re.Pattern]]] = None,
        sort: Union[Callable[[str], int], Callable[[str], str]] = basic_sort,
        reverse: bool = False,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory from which to yield files
            exclusions: File path regular expressions to exclude
            inclusions: File path regular expressions to include
            sort: Function with which to sort file paths
            reverse: Whether to reverse file path sort order
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.directory = validate_input_directory(directory)
        """Directory from which to yield files"""

        if exclusions is None:
            exclusions = set()
        exclusions |= self.cls_exclusions
        self.exclusions: set[re.Pattern] = set()
        """File path regular expressions to exclude"""
        for exclusion in exclusions:
            if isinstance(exclusion, str):
                exclusion = re.compile(exclusion)
            elif not isinstance(exclusion, re.Pattern):
                raise TypeError(
                    f"Exclusion must be str or re.Pattern, not {type(exclusion)}"
                )
            self.exclusions.add(exclusion)

        self.inclusions: Optional[set[re.Pattern]] = None
        """File path regular expressions to include"""
        if inclusions is not None:
            self.inclusions = set()
            """File path regular expressions to include"""
            for inclusion in inclusions:
                if isinstance(inclusion, str):
                    inclusion = re.compile(inclusion)
                elif not isinstance(inclusion, re.Pattern):
                    raise TypeError(
                        f"Inclusion must be str or re.Pattern, not {type(inclusion)}"
                    )
                self.inclusions.add(inclusion)

        self.sort = sort
        """Function with which to sort file paths"""
        self.reverse = reverse
        """Whether to reverse file path sort order"""

        # Store list of file_paths
        file_paths = self.scan_directory(self.directory, self.directory)
        file_paths.sort(
            key=lambda file_path: self.sort(str(file_path.relative_to(self.directory))),
            reverse=self.reverse,
        )
        self.file_paths = file_paths
        """File paths to be yielded"""
        self.index = 0
        """Index of next file path to be yielded"""

    def scan_directory(self, root_directory: Path, directory: Path) -> list[Path]:
        """Recursively scan directory for files.

        Arguments:
            root_directory: Root directory being scanned overall
            directory: Directory to scan presently
        Returns:
            List of file paths within directory
        """
        file_paths = []
        for file_path in [f for f in directory.iterdir() if f.is_file()]:
            relative_path = file_path.relative_to(root_directory)
            if any(e.match(str(relative_path)) for e in self.exclusions):
                continue
            if self.inclusions is not None:
                if not any(i.match(str(relative_path)) for i in self.inclusions):
                    continue
            file_paths.append(file_path)
        for subdirectory_path in [d for d in directory.iterdir() if d.is_dir()]:
            file_paths.extend(self.scan_directory(root_directory, subdirectory_path))

        return file_paths

    def __next__(self):
        """Yield next image."""
        if self.index < len(self.file_paths):
            file_path = self.file_paths[self.index]
            self.index += 1
            relative_path = file_path.parent.relative_to(self.directory)
            if relative_path == Path("."):
                relative_path = None
            return PipeImage(path=file_path, location=relative_path)
        raise StopIteration

    def __repr__(self):
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"directory={self.directory},"
            f"exclusions={self.exclusions},"
            f"inclusions={self.inclusions},"
            f"sort={self.sort},"
            f"reverse={self.reverse})"
        )
