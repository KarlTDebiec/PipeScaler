#!/usr/bin/env python
#   pipescaler/mergers/color_to_alpha_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from logging import info
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.core import Merger, validate_image


class ColorToAlphaMerger(Merger):
    """
    Merges alpha and color images into a single image with transparency, treating a
    defined color as transparent.
    """

    def __init__(self, alpha_color: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.alpha_color = alpha_color

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        # Read images
        color_image = validate_image(infiles["color"], ["RGB"])
        alpha_image = validate_image(infiles["alpha"], "L")

        # Merge images
        color_datum = np.array(color_image)
        alpha_datum = np.array(alpha_image)
        transparent_pixels = alpha_datum == 255
        output_datum = np.copy(color_datum)
        output_datum[transparent_pixels] = self.alpha_color
        output_image = Image.fromarray(output_datum)

        # Write image
        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    @property
    def inlets(self):
        return ["color", "alpha"]
