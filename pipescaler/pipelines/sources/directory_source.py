#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a directory."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Optional, Type, Union

from pipescaler.common import PathLike, validate_input_directory
from pipescaler.core.pipelines import PipeImage, PipeObject, Source
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
        pipe_object_cls: Type[PipeObject] = PipeImage,
        sort: Union[Callable[[str], int], Callable[[str], str]] = basic_sort,
        reverse: bool = False,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory from which to yield files
            exclusions: File path regular expressions to exclude
            inclusions: File path regular expressions to include
            pipe_object_cls: Class to use for yielded objects
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
        self.pipe_object_cls = pipe_object_cls
        """Class to use for yielded objects"""
        self.sort = sort
        """Function with which to sort file paths"""
        self.reverse = reverse
        """Whether to reverse file path sort order"""
        self.pipe_cls = PipeImage

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

    def __next__(self) -> PipeObject:
        """Yield next image."""
        if self.index < len(self.file_paths):
            file_path = self.file_paths[self.index]
            self.index += 1
            relative_path: Optional[Path] = file_path.parent.relative_to(self.directory)
            if relative_path == Path("."):
                relative_path = None
            return self.pipe_object_cls(path=file_path, location=relative_path)
        raise StopIteration

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
            if self.inclusions is not None:
                if not any(i.match(str(relative_path)) for i in self.inclusions):
                    continue
            file_paths.append(file_path)
        for subdirectory_path in [d for d in directory.iterdir() if d.is_dir()]:
            file_paths.extend(self.scan_directory(root_directory, subdirectory_path))

        return file_paths

    @classmethod
    def parse_exclusions(
        cls, exclusions: Optional[set[Union[str, re.Pattern]]]
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
        cls, inclusions: Optional[set[Union[str, re.Pattern]]]
    ) -> Optional[set[re.Pattern]]:
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
