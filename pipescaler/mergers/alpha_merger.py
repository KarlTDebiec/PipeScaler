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

from pipescaler.core import Merger, UnsupportedImageModeError, remove_palette_from_image


####################################### CLASSES ########################################
class AlphaMerger(Merger):

    # region Builtins

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        # Read images
        color_image = Image.open(infiles["color"])
        if color_image.mode == "P":
            color_image = remove_palette_from_image(color_image)
        if color_image.mode not in ("L", "RGB"):
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
        if color_image.mode == "L":
            output_datum = np.zeros((*color_datum.shape[:-1], 2), np.uint8)
        else:
            output_datum = np.zeros((*color_datum.shape[:-1], 4), np.uint8)
        output_datum[:, :, :-1] = color_datum
        output_datum[:, :, -1] = alpha_datum
        output_image = Image.fromarray(output_datum)

        # Write image
        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    # endregion

    # region Properties

    @property
    def inlets(self):
        return ["color", "alpha"]

    # endregion
