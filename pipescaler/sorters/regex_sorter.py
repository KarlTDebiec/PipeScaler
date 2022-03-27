#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on filename using a regular expression."""
from __future__ import annotations

import re
from logging import info
from os.path import basename, dirname
from typing import Any

from pipescaler.core import Sorter


class RegexSorter(Sorter):
    """Sorts image based on filename using a regular expression."""

    def __init__(self, regex: str, **kwargs: Any) -> None:
        """
        Validate and store static configuration
            Arguments:
                regex: Sort as 'matched' if image name matches this regular expression
                **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.regex = re.compile(regex)

    def __call__(self, infile: str) -> str:
        """
        Sort image based on filename using a regular expression

        Arguments:
            infile: Input image

        Returns:
            Outlet
        """
        # Identify image
        name = basename(dirname(infile))

        # Sort image
        if self.regex.match(name):
            info(f"{self}: '{name}' matches '{self.regex.pattern}'")
            return "matched"
        info(f"{self}: '{name}' does not match '{self.regex.pattern}'")
        return "unmatched"

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of stage"""
        return ["matched", "unmatched"]
