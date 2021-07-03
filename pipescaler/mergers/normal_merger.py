#!/usr/bin/env python
#   pipescaler/mergers/normal_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image

from pipescaler.core import Merger


####################################### CLASSES ########################################
class NormalMerger(Merger):

    # region Builtins

    def __call__(self, outfile: str, verbosity: int = 1, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        r_datum = np.array(Image.open(infiles["r"]).convert("L"), np.float) - 128
        g_datum = np.array(Image.open(infiles["g"]).convert("L"), np.float) - 128
        b_datum = np.array(Image.open(infiles["b"]).convert("L"), np.float) - 128

        b_datum[b_datum < 0] = 0
        mag = np.sqrt(r_datum ** 2 + g_datum ** 2 + b_datum ** 2)
        r_datum = (((r_datum / mag) * 128) + 128).astype(np.uint8)
        g_datum = (((g_datum / mag) * 128) + 128).astype(np.uint8)
        b_datum = (((b_datum / mag) * 128) + 128).astype(np.uint8)
        b_datum[b_datum == 0] = 255

        rgb_datum = np.zeros((r_datum.shape[0], r_datum.shape[1], 3), np.uint8)
        rgb_datum[:, :, 0] = r_datum
        rgb_datum[:, :, 1] = g_datum
        rgb_datum[:, :, 2] = b_datum
        rgb_image = Image.fromarray(rgb_datum)

        if verbosity >= 1:
            print(f"Saving rgb to '{outfile}'")
        rgb_image.save(outfile)

    # endregion

    # region Properties

    @property
    def inlets(self):
        return ["r", "g", "b"]

    # endregion
