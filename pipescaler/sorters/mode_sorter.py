#!/usr/bin/env python
#   pipescaler/sorters/mode_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from logging import info
from typing import List

from pipescaler.core import Sorter, validate_image


class ModeSorter(Sorter):
    """Sorts image based on mode."""

    def __call__(self, infile: str) -> str:

        # Read image
        image = validate_image(infile, ["L", "LA", "RGB", "RBGA"])

        # Sort image
        if image.mode == "RGBA":
            info(f"{self}: '{infile}' matches 'RGBA'")
            return "rgba"
        elif image.mode == "RGB":
            info(f"{self}: {infile}' matches 'RGB'")
            return "rgb"
        elif image.mode == "LA":
            info(f"{self}: {infile}' matches 'LA'")
            return "la"
        else:
            info(f"{self}: {infile}' matches 'L'")
            return "l"

    @property
    def outlets(self) -> List[str]:
        return ["rgba", "rgb", "la", "l"]
