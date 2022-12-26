#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on filename using a set of configured lists."""
from __future__ import annotations

from logging import info
from pathlib import Path
from typing import Any, Iterable

from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.sorter import Sorter


class ListSorter(Sorter):
    """Sorts image based on filename using a set of configured lists."""

    exclusions = {".DS_Store", "desktop"}
    """Base filenames to exclude"""

    def __init__(self, **outlets: Any) -> None:
        """Validate configuration and initialize.

        Arguments:
            **outlets: Outlets to which images may be sorted; keys are outlet names
              and values are paths to directories or text files; if path is to a
              directory, images with names matching the files within that directory will
              be sorted to that outlet; if path is to a text file, images with names
              matching a line in the file will be sorted to that outlet
        """
        self._outlets = tuple(sorted((outlets.keys())))
        self.outlets_by_filename = {}

        for outlet, paths in outlets.items():
            if not isinstance(paths, list):
                paths = [paths]
            for path in paths:
                path = Path(path).resolve()
                if path.exists():
                    names: Iterable[str] = []
                    if path.is_file():
                        with open(path, "r", encoding="utf8") as infile:
                            names = (
                                line.strip()
                                for line in infile.readlines()
                                if not line.startswith("#")
                            )
                    if path.is_dir():
                        names = (f.stem for f in path.iterdir() if f.is_file())
                    for name in names:
                        if name in self.exclusions:
                            continue
                        self.outlets_by_filename[name] = outlet

    def __call__(self, object: PipeImage) -> str:
        """Get the outlet to which an image should be sorted.

        Arguments:
            object: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        outlet = self.outlets_by_filename.get(object.name, None)
        if outlet is not None:
            info(f"{self}: '{object.location_name}' matches '{outlet}'")
        else:
            info(f"{self}: '{object.location_name}' does not match any outlet")
            outlet = "none"
        return outlet

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return self._outlets
