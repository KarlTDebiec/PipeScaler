#!/usr/bin/env python
#   pipescaler/sorters/list_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from logging import info, warning
from os.path import basename, dirname
from pprint import pformat
from typing import Any, Dict, List

from pipescaler.core import Sorter, parse_file_list


class ListSorter(Sorter):
    """Sorts image based on filename using a set of configured lists."""

    exclusions = {".DS_Store", "desktop"}

    def __init__(self, outlets: Dict[str, List[str]], **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self._outlets = list(outlets.keys())
        self.outlets_by_filename = {}

        # Organize downstream outlets
        duplicates = {}
        for outlet in self.outlets:
            for filename in parse_file_list(
                outlets.get(outlet, []), False, self.exclusions
            ):
                if filename in self.outlets_by_filename:
                    duplicates[filename] = duplicates.get(
                        filename, [self.outlets_by_filename[filename]]
                    ) + [outlet]
                else:
                    self.outlets_by_filename[filename] = outlet
        if len(duplicates) != 0:
            sorted_duplicates = {
                key: sorted(duplicates[key]) for key in sorted(list(duplicates.keys()))
            }
            warning(
                f"{self}: multiple outlets specified for the following filenames: "
                f"{pformat(sorted_duplicates)}"
            )

    def __call__(self, infile: str) -> str:
        # Identify image
        name = basename(dirname(infile))

        # Sort image
        outlet = self.outlets_by_filename.get(name, None)
        if outlet is not None:
            info(f"{self}: '{name}' matches '{outlet}'")
        else:
            info(f"{self}: '{name}' does not match any outlet")
        return outlet

    @property
    def outlets(self):
        return self._outlets
