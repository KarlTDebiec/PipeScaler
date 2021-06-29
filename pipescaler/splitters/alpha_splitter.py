#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import Any

from pipescaler.core import Splitter


####################################### CLASSES ########################################
class AlphaSplitter(Splitter):

    # region Properties

    @property
    def outlets(self):
        return ["rgb", "a"]

    # endregion

    # region Class Methods

    @classmethod
    def process_file(cls, infile: str, verbosity: int = 1, **kwargs: Any) -> None:
        raise NotImplementedError()

    # endregion
