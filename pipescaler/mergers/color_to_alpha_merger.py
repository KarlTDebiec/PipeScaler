#!/usr/bin/env python
#   pipescaler/mergers/color_to_alpha_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from logging import info
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.core import Merger, UnsupportedImageModeError, remove_palette_from_image


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
        color_image = Image.open(infiles["color"])
        if color_image.mode == "P":
            color_image = remove_palette_from_image(color_image)
        if color_image.mode != "RGB":
            raise UnsupportedImageModeError(
                f"Image mode '{color_image.mode}' of image '{infiles['color']}'"
                f" is not supported by {type(self)}"
            )
        alpha_image = Image.open(infiles["alpha"])
        if alpha_image.mode == "P":
            alpha_image = remove_palette_from_image(alpha_image)
        if alpha_image.mode != "L":
            raise UnsupportedImageModeError(
                f"Image mode '{alpha_image.mode}' of image '{infiles['alpha']}'"
                f" is not supported by {type(self)}"
            )

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
