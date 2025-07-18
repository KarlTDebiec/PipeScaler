#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges x, y, and z images into a single normal map image."""

from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.image.core.operators import ImageMerger
from pipescaler.image.core.validation import validate_image


class NormalMerger(ImageMerger):
    """Merges x, y, and z images into a single normal map image."""

    def __call__(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            input_images: Input images
        Returns:
            Merged output image
        """
        x_img = validate_image(input_images[0], self.inputs()["x"])
        y_img = validate_image(input_images[1], self.inputs()["y"])
        z_img = validate_image(input_images[2], self.inputs()["z"])

        x_arr = np.clip(np.array(x_img, float) - 128, -128, 127)
        y_arr = np.clip(np.array(y_img, float) - 128, -128, 127)
        z_arr = np.clip(np.array(z_img, float) / 2, 0, 127)
        magnitude = np.sqrt(x_arr**2 + y_arr**2 + z_arr**2)
        x_arr = np.clip(((x_arr / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        y_arr = np.clip(((y_arr / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        z_arr = np.clip(((z_arr / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        output_arr = np.zeros((*x_arr.shape, 3), np.uint8)
        output_arr[:, :, 0] = x_arr
        output_arr[:, :, 1] = y_arr
        output_arr[:, :, 2] = z_arr
        output_img = Image.fromarray(output_arr)

        return output_img

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "x": ("L",),
            "y": ("L",),
            "z": ("L",),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("RGB",),
        }
