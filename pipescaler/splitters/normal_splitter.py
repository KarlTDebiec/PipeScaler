#!/usr/bin/env python
#   pipescaler/splitter/normal_splitter.py
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
class NormalSplitter(Splitter):

    # region Builtins

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
        input_datum = np.array(input_image)
        x_datum = input_datum[:, :, 0]
        y_datum = input_datum[:, :, 1]
        z_datum = np.clip(
            (input_datum[:, :, 2].astype(float) - 128) * 2, 0, 255
        ).astype(np.uint8)
        x_image = Image.fromarray(x_datum)
        y_image = Image.fromarray(y_datum)
        z_image = Image.fromarray(z_datum)

        # Write images
        x_image.save(outfiles["x"])
        info(f"'{self}: '{outfiles['x']}' saved")
        y_image.save(outfiles["y"])
        info(f"'{self}: '{outfiles['y']}' saved")
        z_image.save(outfiles["z"])
        info(f"'{self}: '{outfiles['z']}' saved")

        return outfiles

    # endregion

    # region Properties

    @property
    def outlets(self):
        return ["x", "y", "z"]

    # endregion
