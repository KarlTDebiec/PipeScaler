#!/usr/bin/env python
#   pipescaler/mergers/normal_merger.py
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


class NormalMerger(Merger):
    """Merges x, y, and z images into a single normal map image."""

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        infiles = {k: kwargs.get(k) for k in self.inlets}

        # Read images
        x_image = validate_image(infiles["x"], "L")
        y_image = validate_image(infiles["y"], "L")
        z_image = validate_image(infiles["z"], "L")

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

    @property
    def inlets(self):
        return ["x", "y", "z"]
