#!/usr/bin/env python
#   pipescaler/mergers/color_to_alpha_merger.py
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
class ColorToAlphaMerger(Merger):

    # region Builtins

    def __init__(self, alpha_color: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.alpha_color = alpha_color

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        # Read images
        rgb = Image.open(infiles["rgb"]).convert("RGB")
        a = Image.open(infiles["a"]).convert("L")

        # Merge images
        rgb_datum = np.array(rgb)
        a_datum = np.array(a)
        transparent_pixels = a_datum == 255
        rgb_datum[transparent_pixels] = self.alpha_color
        rgb = Image.fromarray(rgb_datum)

        # Write image
        rgb.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    # endregion

    # region Properties

    @property
    def inlets(self):
        return ["rgb", "a"]

    # endregion
