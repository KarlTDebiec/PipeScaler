#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from logging import info
from typing import Any, Dict

import numpy as np
from PIL import Image

from pipescaler.core import Splitter, validate_image


class AlphaSplitter(Splitter):
    """Splits image with transparency into separate alpha and color images."""

    def __init__(self, smart_fill: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.smart_fill = smart_fill

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        outfiles = {k: kwargs.get(k) for k in self.outlets}

        # Read image
        input_image = validate_image(infile, ["LA", "RGBA"])

        # Split image
        input_datum = np.array(input_image)
        color_datum = np.squeeze(input_datum[:, :, :-1])
        alpha_datum = input_datum[:, :, -1]
        color_image = Image.fromarray(color_datum)
        alpha_image = Image.fromarray(alpha_datum)

        # Write images
        color_image.save(outfiles["color"])
        info(f"{self}: '{outfiles['color']}' saved")
        alpha_image.save(outfiles["alpha"])
        info(f"{self}: '{outfiles['alpha']}' saved")

        return outfiles

    @property
    def outlets(self):
        return ["color", "alpha"]
