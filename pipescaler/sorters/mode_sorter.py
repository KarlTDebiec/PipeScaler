#!/usr/bin/env python
#   pipescaler/sorters/mode_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from logging import info
from typing import Any, List

from PIL import Image

from pipescaler.core import Sorter, UnsupportedImageModeError, remove_palette_from_image


class ModeSorter(Sorter):
    def __call__(self, infile: str) -> str:

        # Read image
        image = Image.open(infile)
        if image.mode == "P":
            image = remove_palette_from_image(image)

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
        elif image.mode == "L":
            info(f"{self}: {infile}' matches 'L'")
            return "l"
        else:
            raise UnsupportedImageModeError(
                f"Image mode '{image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
            )

    @property
    def outlets(self) -> List[str]:
        return ["rgba", "rgb", "la", "l"]
