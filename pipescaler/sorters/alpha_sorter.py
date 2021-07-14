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

from pipescaler.common import validate_int
from pipescaler.core import Sorter


####################################### CLASSES ########################################
class AlphaSorter(Sorter):

    # region Builtins

    def __init__(self, threshold: int = 255, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.threshold = validate_int(threshold, 0, 255)

    def __call__(self, infile: str) -> str:
        # Read image
        image = Image.open(infile)

        # Sort image
        if image.mode == "RGBA":
            alpha = np.array(image)[:, :, 3]
            if alpha.min() >= self.threshold:
                info(f"{self}: '{infile}' matches 'drop_alpha'")
                return "drop_alpha"
            else:
                info(f"{self}: '{infile}' matches 'drop_alpha'")
                return "keep_alpha"
        elif image.mode in ("RGB", "L"):
            info(f"{self}: {infile}' matches 'no_alpha'")
            return "no_alpha"
        else:
            raise ValueError()

    # endregion

    # region Properties

    @property
    def outlets(self) -> List[str]:
        return ["drop_alpha", "keep_alpha", "no_alpha"]

    # endregion