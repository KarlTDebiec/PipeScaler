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
from typing import Any

from pipescaler.core import Sorter


####################################### CLASSES ########################################
class RegexSorter(Sorter):

    # region Builtins

    def __init__(self, regex: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.regex = re.compile(regex)

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["matched", "unmatched"]

    # endregion

    # region Class Methods

    @classmethod
    def process_file(cls, infile: str, verbosity: int = 1, **kwargs: Any) -> None:
        raise NotImplementedError()

    #
