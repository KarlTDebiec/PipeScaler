#!/usr/bin/env python
#   pipescaler/sorters/regex_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

import re
from logging import info
from os.path import basename, dirname
from typing import Any, List

from pipescaler.core import Sorter


class RegexSorter(Sorter):
    """Sorts image based on filename using a regular expression."""

    def __init__(self, regex: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.regex = re.compile(regex)

    def __call__(self, infile: str) -> str:
        # Identify image
        name = basename(dirname(infile))

        # Sort image
        if self.regex.match(name):
            info(f"{self}: '{name}' matches '{self.regex.pattern}'")
            return "matched"
        else:
            info(f"{self}: '{name}' does not match '{self.regex.pattern}'")
            return "unmatched"

    @property
    def outlets(self) -> List[str]:
        return ["matched", "unmatched"]
