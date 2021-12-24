#!/usr/bin/env python
#   pipescaler/mergers/normal_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Merges x, y, and z images into a single normal map image"""
from __future__ import annotations

from logging import info
from typing import Any, List

import numpy as np
from PIL import Image

from pipescaler.core import Merger, validate_image


class NormalMerger(Merger):
    """Merges x, y, and z images into a single normal map image."""

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        """
        Merge images

        Args:
            outfile: Output image
            **kwargs: Additional keyword arguments
        """
        self.merge(outfile, **{k: kwargs.get(k) for k in self.inlets})

    def merge(self, x: str, y: str, z: str, outfile: str) -> None:
        """
        Merge x, y, and z images into a single normal map image

        Args:
            x: X infile
            y: Y infile
            z: Z infile
            outfile: Output file
        """
        # Read images
        x_image = validate_image(x, "L")
        y_image = validate_image(y, "L")
        z_image = validate_image(z, "L")

        # Merge images
        x_array = np.clip(np.array(x_image, float) - 128, -128, 127)
        y_array = np.clip(np.array(y_image, float) - 128, -128, 127)
        z_array = np.clip(np.array(z_image, float) / 2, 0, 127)
        magnitude = np.sqrt(x_array ** 2 + y_array ** 2 + z_array ** 2)
        x_array = np.clip(((x_array / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        y_array = np.clip(((y_array / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        z_array = np.clip(((z_array / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        output_array = np.zeros((*x_array.shape, 3), np.uint8)
        output_array[:, :, 0] = x_array
        output_array[:, :, 1] = y_array
        output_array[:, :, 2] = z_array
        output_image = Image.fromarray(output_array)

        # Write image
        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["x", "y", "z"]
