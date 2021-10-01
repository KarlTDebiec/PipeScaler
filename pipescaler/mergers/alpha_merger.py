#!/usr/bin/env python
#   pipescaler/mergers/alpha_merger.py
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


class AlphaMerger(Merger):
    """Merges alpha and color images into a single image with transparency."""

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        # Read images
        color_image = validate_image(infiles["color"], ["L", "RGB"])
        alpha_image = validate_image(infiles["alpha"], "L")

        # Merge images
        color_datum = np.array(color_image)
        alpha_datum = np.array(alpha_image)
        if color_image.mode == "L":
            output_datum = np.zeros((*color_datum.shape, 2), np.uint8)
            output_datum[:, :, 0] = color_datum
        else:
            output_datum = np.zeros((*color_datum.shape[:-1], 4), np.uint8)
            output_datum[:, :, :-1] = color_datum
        output_datum[:, :, -1] = alpha_datum
        output_image = Image.fromarray(output_datum)

        # Write image
        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    @property
    def inlets(self):
        return ["color", "alpha"]
