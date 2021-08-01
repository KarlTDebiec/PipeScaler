#!/usr/bin/env python
#   pipescaler/sorters/alpha_sorter.py
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

import numpy as np
from PIL import Image

from pipescaler.common import validate_float, validate_int
from pipescaler.core import Sorter


####################################### CLASSES ########################################
class GrayscaleSorter(Sorter):

    # region Builtins

    def __init__(
        self, mean_threshold: float = 1, max_threshold: float = 10, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.mean_threshold = validate_float(mean_threshold, 0, 255)
        self.max_threshold = validate_int(max_threshold, 0, 255)

    def __call__(self, infile: str) -> str:
        # Read image
        image = Image.open(infile)

        # Sort image
        if image.mode == "RGBA":
            info(f"{self}: {infile}' matches 'rgba'")
            return "rgba"
        elif image.mode == "RGB":
            rgb = np.array(image)[:, :, :3].astype(np.int)
            l = np.array(Image.fromarray(np.array(image)[:, :, :3]).convert("L"))
            diff = np.abs(rgb.transpose() - l.transpose())
            if diff.mean() <= self.mean_threshold and diff.max() <= self.max_threshold:
                info(f"{self}: '{infile}' matches 'drop_rgb'")
                return "drop_rgb"
            else:
                info(f"{self}: '{infile}' matches 'keep_rgb'")
                return "keep_rgb"
        elif image.mode == "L":
            info(f"{self}: {infile}' matches 'no_rgb'")
            return "no_rgb"
        else:
            raise ValueError()

    # endregion

    # region Properties

    @property
    def outlets(self) -> List[str]:
        return ["drop_rgb", "keep_rgb", "no_rgb", "rgba"]

    # endregion
