#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges alpha and color images into a single image with transparency."""

from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.image.core.operators import ImageMerger
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image


class AlphaMerger(ImageMerger):
    """Merges color and alpha images into a single image with transparency."""

    def __call__(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            input_images: Input images
        Returns:
            Merged output image
        """
        color_img = validate_image(input_images[0], self.inputs()["color"])
        alpha_img = validate_image(input_images[1], self.inputs()["alpha"])

        color_arr = np.array(color_img)
        if alpha_img.mode == "L":
            alpha_arr = np.array(alpha_img)
        else:
            alpha_arr = np.array(alpha_img.convert("L"))
        if color_img.mode == "L":
            output_arr = np.zeros((*color_arr.shape, 2), np.uint8)
            output_arr[:, :, 0] = color_arr
        else:
            output_arr = np.zeros((*color_arr.shape[:-1], 4), np.uint8)
            output_arr[:, :, :-1] = color_arr
        output_arr[:, :, -1] = alpha_arr
        output_img = Image.fromarray(output_arr)

        return output_img

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "color": ("L", "RGB"),
            "alpha": ("1", "L"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("LA", "RGBA"),
        }
