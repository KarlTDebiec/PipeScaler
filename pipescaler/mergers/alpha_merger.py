#!/usr/bin/env python
#   pipescaler/mergers/alpha_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Merges alpha and color images into a single image with transparency"""
from __future__ import annotations

from logging import info
from typing import Any, List

import numpy as np
from PIL import Image

from pipescaler.core import Merger, validate_image


class AlphaMerger(Merger):
    """Merges alpha and color images into a single image with transparency"""

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        """
        Merge images

        Args:
            outfile: Output image
            **kwargs: Additional keyword arguments
        """
        self.merge(outfile=outfile, **{k: kwargs.get(k) for k in self.inlets})

    def merge(self, color: str, alpha: str, outfile: str) -> None:
        """
        Merge color and alpha images into a single image with transparency

        Args:
            color: Color infile
            alpha: Alpha infile
            outfile: Output file
        """
        # Read images
        color_image = validate_image(color, ["L", "RGB"])
        alpha_image = validate_image(alpha, "L")

        # Merge images
        color_array = np.array(color_image)
        alpha_array = np.array(alpha_image)
        if color_image.mode == "L":
            output_array = np.zeros((*color_array.shape, 2), np.uint8)
            output_array[:, :, 0] = color_array
        else:
            output_array = np.zeros((*color_array.shape[:-1], 4), np.uint8)
            output_array[:, :, :-1] = color_array
        output_array[:, :, -1] = alpha_array
        output_image = Image.fromarray(output_array)

        # Write image
        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["color", "alpha"]
