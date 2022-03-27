#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Sorts image based on filename using a set of configured lists."""
from __future__ import annotations

from logging import info, warning
from os.path import basename, dirname, splitext
from pprint import pformat
from typing import Any, Dict, List, Optional

from pipescaler.common import validate_output_directory
from pipescaler.core import Sorter, get_files


class ListSorter(Sorter):
    """Sorts image based on filename using a set of configured lists."""

    exclusions = {".DS_Store", "desktop"}
    """Base filenames to exclude"""

    def __init__(
        self,
        outlets: Dict[str, List[str]],
        wip_directory: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store configuration

        Arguments:
            outlets: Outlet configuration
            wip_directory: Work-in-progress directory; workaround used to handle
              potential file locations both inside and outside a pipeline's
              wip_directory
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self._outlets = list(outlets.keys())
        self.outlets_by_filename = {}
        self.wip_directory = None
        if wip_directory is not None:
            self.wip_directory = validate_output_directory(wip_directory)

        # Organize downstream outlets
        duplicates = {}
        for outlet in self.outlets:
            for filename in get_files(
                outlets.get(outlet, []),
                style="base",
                exclusions=self.exclusions,
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
        """
        Sort image based on filename using a set of configured lists

        Arguments:
            infile: Input image

        Returns:
            Outlet
        """
        # Identify image
        if self.wip_directory is not None and not infile.startswith(self.wip_directory):
            name = splitext(basename(infile))[0]
        else:
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
        """Outlets that flow out of stage"""
        return self._outlets
