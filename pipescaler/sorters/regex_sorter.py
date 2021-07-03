#!/usr/bin/env python
#   pipescaler/sorters/regex_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

import re
from os.path import basename, dirname
from typing import Any

from pipescaler.core import Sorter


####################################### CLASSES ########################################
class RegexSorter(Sorter):

    # region Builtins

    def __init__(self, regex: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.regex = re.compile(regex)

    def __call__(self, infile: str, verbosity: int = 1, **kwargs: Any) -> str:
        name = basename(dirname(infile))
        if self.regex.match(name):
            if verbosity >= 1:
                print(f"'{name}' matches {self.regex.pattern}")
            return "matched"
        else:
            if verbosity >= 1:
                print(f"'{name}' does not match {self.regex.pattern}")
            return "unmatched"

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["matched", "unmatched"]

    # endregion
