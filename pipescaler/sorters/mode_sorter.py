#!/usr/bin/env python
#   pipescaler/sorters/mode_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import Any, Dict

from PIL import Image

from pipescaler.core import Sorter


####################################### CLASSES ########################################
class ModeSorter(Sorter):

    # region Builtins

    def __call__(self, infile: str, verbosity: int = 1, **kwargs: Any) -> str:
        image = Image.open(infile)
        if image.mode == "rgba":
            return "rgba"
        elif image.mode == "rgb":
            return "rgb"
        elif image.mode == "l":
            return "l"

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["rgba", "rgb", "l"]

    # endregion
