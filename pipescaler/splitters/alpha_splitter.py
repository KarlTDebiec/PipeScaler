#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
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
class AlphaSplitter(Splitter):

    # region Builtins

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        outfiles = {k: kwargs.get(k) for k in self.outlets}

        # Read image
        input_image = Image.open(infile)
        if input_image.mode == "P":
            input_image = remove_palette_from_image(input_image)
        if input_image.mode not in ("LA", "RGBA"):
            raise UnsupportedImageModeError(
                f"Image mode '{input_image.mode}' of image '{infile}'"
                f" is not supported by {type(self)}"
            )

        # Split image
        if input_image.mode == "LA":
            color_image = Image.fromarray(np.array(input_image)[:, :, 0])
            alpha_image = Image.fromarray(np.array(input_image)[:, :, 1])
        else:
            color_image = Image.fromarray(np.array(input_image)[:, :, :3])
            alpha_image = Image.fromarray(np.array(input_image)[:, :, 3])

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
