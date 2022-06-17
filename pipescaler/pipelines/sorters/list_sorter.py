#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on filename using a set of configured lists."""
from __future__ import annotations

from logging import info
from pathlib import Path
from typing import Any

from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.sorter import Sorter


class ListSorter(Sorter):
    """Sorts image based on filename using a set of configured lists."""

    exclusions = {".DS_Store", "desktop"}
    """Base filenames to exclude"""

    def __init__(
        self,
        **outlets: Any,
    ) -> None:
        self._outlets = tuple(sorted((outlets.keys())))
        self.outlets_by_filename = {}

        # Organize downstream outlets
        duplicates = {}
        for outlet, paths in outlets.items():
            if not isinstance(paths, list):
                paths = [paths]
            for path in paths:
                path = Path(path).absolute()
                if path.exists():
                    names = []
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

    def __call__(self, pipe_image: PipeImage) -> str:
        outlet = self.outlets_by_filename.get(pipe_image.name, None)
        if outlet is not None:
            info(f"{self}: '{pipe_image.name}' matches '{outlet}'")
        else:
            info(f"{self}: '{pipe_image.name}' does not match any outlet")
        return outlet

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets that flow out of stage."""
        return self._outlets
