#!/usr/bin/env python
#   pipescaler/mergers/alpha_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from logging import info
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.core import Merger


####################################### CLASSES ########################################
class AlphaMerger(Merger):

    # region Builtins

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        # Read images
        rgb_datum = np.array(Image.open(infiles["rgb"]).convert("RGB"))
        a_datum = np.array(Image.open(infiles["a"]).convert("L"))

        # Merge images
        rgba_datum = np.zeros((rgb_datum.shape[0], rgb_datum.shape[1], 4), np.uint8)
        rgba_datum[:, :, :3] = rgb_datum
        rgba_datum[:, :, 3] = a_datum
        rgba_image = Image.fromarray(rgba_datum)

        # Write image
        rgba_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    # endregion

    # region Properties

    @property
    def inlets(self):
        return ["rgb", "a"]

    # endregion
