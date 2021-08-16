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

from logging import info
from typing import Any

import numpy as np
from PIL import Image

from pipescaler.core import Merger, UnsupportedImageModeError, remove_palette_from_image


####################################### CLASSES ########################################
class NormalMerger(Merger):

    # region Builtins

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        # Read images
        x_image = Image.open(infiles["x"])
        if x_image.mode == "P":
            x_image = remove_palette_from_image(x_image)
        if x_image.mode != "L":
            raise UnsupportedImageModeError(
                f"Image mode '{x_image.mode}' of image '{infiles['x']}'"
                f" is not supported by {type(self)}"
            )
        y_image = Image.open(infiles["y"])
        if y_image.mode == "P":
            y_image = remove_palette_from_image(y_image)
        if y_image.mode != "L":
            raise UnsupportedImageModeError(
                f"Image mode '{y_image.mode}' of image '{infiles['y']}'"
                f" is not supported by {type(self)}"
            )
        z_image = Image.open(infiles["z"])
        if z_image.mode == "P":
            z_image = remove_palette_from_image(z_image)
        if z_image.mode != "L":
            raise UnsupportedImageModeError(
                f"Image mode '{z_image.mode}' of image '{infiles['z']}'"
                f" is not supported by {type(self)}"
            )

        # Merge images
        x_datum = np.clip(np.array(x_image, float) - 128, -128, 127)
        y_datum = np.clip(np.array(y_image, float) - 128, -128, 127)
        z_datum = np.clip(np.array(z_image, float) / 2, 0, 127)
        magnitude = np.sqrt(x_datum ** 2 + y_datum ** 2 + z_datum ** 2)
        x_datum = np.clip(((x_datum / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        y_datum = np.clip(((y_datum / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        z_datum = np.clip(((z_datum / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        output_datum = np.zeros((*x_datum.shape, 3), np.uint8)
        output_datum[:, :, 0] = x_datum
        output_datum[:, :, 1] = y_datum
        output_datum[:, :, 2] = z_datum
        output_image = Image.fromarray(output_datum)

        # Write image
        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    # endregion

    # region Properties

    @property
    def inlets(self):
        return ["x", "y", "z"]

    # endregion
