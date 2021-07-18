#!/usr/bin/env python
#   pipescaler/splitter/color_to_alpha_splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from logging import info
from typing import Any, Dict

import numpy as np
from PIL import Image

from pipescaler.core import Splitter


####################################### CLASSES ########################################
class ColorToAlphaSplitter(Splitter):

    # region Builtins

    def __init__(self, alpha_color: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.alpha_color = alpha_color

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        outfiles = {k: kwargs.get(k) for k in self.outlets}

        # Read image
        rgb = Image.open(infile).convert("RGB")

        # Split images
        rgb_datum = np.array(rgb)
        a_datum = np.zeros((rgb_datum.shape[0], rgb_datum.shape[1]), np.uint8)
        transparent_pixels = (rgb_datum == [255, 0, 255]).all(axis=2)
        a_datum[transparent_pixels] = 255
        rgb_datum[transparent_pixels, :] = 0
        rgb = Image.fromarray(rgb_datum)
        a = Image.fromarray(a_datum)

        # Write images
        rgb.save(outfiles["rgb"])
        info(f"{self}: '{outfiles['rgb']}' saved")
        a.save(outfiles["a"])
        info(f"{self}: '{outfiles['a']}' saved")

        return outfiles

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["rgb", "a"]

    # endregion
