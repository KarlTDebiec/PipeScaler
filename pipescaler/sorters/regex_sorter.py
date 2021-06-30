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
from typing import Any, Dict

from pipescaler.core import Sorter


####################################### CLASSES ########################################
class RegexSorter(Sorter):

    # region Builtins

    def __init__(self, regex: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.regex = re.compile(regex)

    def __call__(self, infile: str, verbosity: int = 1, **kwargs: Any) -> str:
        if self.regex.match(infile):
            return "matched"
        else:
            return "unmatched"

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["matched", "unmatched"]

    # endregion
