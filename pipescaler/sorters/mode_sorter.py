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

from logging import info
from typing import Any, List

from PIL import Image

from pipescaler.core import Sorter


####################################### CLASSES ########################################
class ModeSorter(Sorter):

    # region Builtins

    def __call__(self, infile: str) -> str:

        # Read image
        image = Image.open(infile)

        # Sort image
        if image.mode == "RGBA":
            info(f"{self}: '{infile}' matches 'RGBA'")
            return "rgba"
        elif image.mode == "RGB":
            info(f"{self}: {infile}' matches 'RGB'")
            return "rgb"
        elif image.mode == "L":
            info(f"{self}: {infile}' matches 'L'")
            return "l"
        else:
            raise ValueError()

    # endregion

    # region Properties

    @property
    def outlets(self) -> List[str]:
        return ["rgba", "rgb", "l"]

    # endregion
