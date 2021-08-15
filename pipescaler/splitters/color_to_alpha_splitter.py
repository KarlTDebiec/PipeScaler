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

from pipescaler.core import (
    Splitter,
    UnsupportedImageModeError,
    remove_palette_from_image,
)


####################################### CLASSES ########################################
class ColorToAlphaSplitter(Splitter):

    # region Builtins

    def __init__(self, alpha_color: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.alpha_color = alpha_color  # TODO: Validate

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        outfiles = {k: kwargs.get(k) for k in self.outlets}

        # Read image
        input_image = Image.open(infile)
        if input_image.mode == "P":
            input_image = remove_palette_from_image(input_image)
        if input_image.mode != "RGB":
            raise UnsupportedImageModeError(
                f"Image mode '{input_image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
            )

        # Split image
        color_datum = np.array(input_image)
        alpha_datum = (
            np.ones((color_datum.shape[0], color_datum.shape[1]), np.uint8) * 255
        )
        transparent_pixels = (color_datum == self.alpha_color).all(axis=2)
        color_datum[transparent_pixels, :] = 0
        # TODO: Implement smart fill
        alpha_datum[transparent_pixels] = 0
        color_image = Image.fromarray(color_datum)
        alpha_image = Image.fromarray(alpha_datum)

        # Write images
        color_image.save(outfiles["color"])
        info(f"{self}: '{outfiles['color']}' saved")
        alpha_image.save(outfiles["alpha"])
        info(f"{self}: '{outfiles['alpha']}' saved")

        return outfiles

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["color", "alpha"]

    # endregion
