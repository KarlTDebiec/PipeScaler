#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sources that yield objects from a directory."""
from __future__ import annotations

import re
from abc import ABC
from pathlib import Path
from typing import Any, Callable

from pipescaler.common import PathLike, validate_input_directory
from pipescaler.core.pipelines.source import Source
from pipescaler.core.sorting import basic_sort


class DirectorySource(Source, ABC):
    """Abstract base class for sources that yield objects from a directory."""

    cls_exclusions = {r".*\.DS_Store$", r".*Thumbs.db$", r".*desktop$"}
    """File paths to exclude"""

    def __init__(
        self,
        directory: PathLike,
        *,
        exclusions: set[str | re.Pattern] | None = None,
        inclusions: set[str | re.Pattern] | None = None,
        sort: Callable[[str], int] | Callable[[str], str] = basic_sort,
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
        self.exclusions = self.parse_exclusions(exclusions)
        """File path regular expressions to exclude"""
        self.inclusions = self.parse_inclusions(inclusions)
        """File path regular expressions to include"""
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

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"directory={self.directory!r}, "
            f"exclusions={self.exclusions!r}, "
            f"inclusions={self.inclusions!r}, "
            f"sort={self.sort!r}, "
            f"reverse={self.reverse!r})"
        )

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
            if self.inclusions:
                if not any(i.match(str(relative_path)) for i in self.inclusions):
                    continue
            file_paths.append(file_path)
        for subdirectory_path in [d for d in directory.iterdir() if d.is_dir()]:
            file_paths.extend(self.scan_directory(root_directory, subdirectory_path))

        return file_paths

    @classmethod
    def parse_exclusions(
        cls, exclusions: set[str | re.Pattern] | None
    ) -> set[re.Pattern]:
        """Parse exclusions.

        Arguments:
            exclusions: Exclusions to parse
        Returns:
            Parsed exclusions
        """
        parsed_exclusions = set()

        for exclusion in cls.cls_exclusions.union(exclusions if exclusions else set()):
            if isinstance(exclusion, str):
                exclusion = re.compile(exclusion)
            elif not isinstance(exclusion, re.Pattern):
                raise TypeError(
                    f"Exclusion must be str or re.Pattern, not {type(exclusion)}"
                )
            parsed_exclusions.add(exclusion)

        return parsed_exclusions

    @classmethod
    def parse_inclusions(
        cls, inclusions: set[str | re.Pattern] | None
    ) -> set[re.Pattern] | None:
        """Parse inclusions.

        Arguments:
            inclusions: Inclusions to parse
        Returns:
            Parsed inclusions
        """
        if inclusions is None:
            return None

        parsed_inclusions = set()
        for inclusion in inclusions:
            if isinstance(inclusion, str):
                inclusion = re.compile(inclusion)
            elif not isinstance(inclusion, re.Pattern):
                raise TypeError(
                    f"Inclusion must be str or re.Pattern, not {type(inclusion)}"
                )
            parsed_inclusions.add(inclusion)

        return parsed_inclusions
