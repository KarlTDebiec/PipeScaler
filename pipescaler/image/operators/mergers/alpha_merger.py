#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Merges alpha and color images into a single image with transparency."""
from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.image.core import validate_image
from pipescaler.image.core.operators import ImageMerger


class AlphaMerger(ImageMerger):
    """Merges color and alpha images into a single image with transparency."""

    def __call__(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            input_images: Input images
        Returns:
            Merged output image
        """
        color_image = validate_image(input_images[0], self.inputs()["color"])
        alpha_image = validate_image(input_images[1], self.inputs()["alpha"])

        color_array = np.array(color_image)
        if alpha_image.mode == "L":
            alpha_array = np.array(alpha_image)
        else:
            alpha_array = np.array(alpha_image.convert("L"))
        if color_image.mode == "L":
            output_array = np.zeros((*color_array.shape, 2), np.uint8)
            output_array[:, :, 0] = color_array
        else:
            output_array = np.zeros((*color_array.shape[:-1], 4), np.uint8)
            output_array[:, :, :-1] = color_array
        output_array[:, :, -1] = alpha_array
        output_image = Image.fromarray(output_array)

        return output_image

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "color": ("L", "RGB"),
            "alpha": ("1", "L"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("LA", "RGBA"),
        }
