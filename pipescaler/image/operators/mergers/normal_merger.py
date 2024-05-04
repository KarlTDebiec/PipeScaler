#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges x, y, and z images into a single normal map image."""
from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.image.core import validate_image
from pipescaler.image.core.operators import ImageMerger


class NormalMerger(ImageMerger):
    """Merges x, y, and z images into a single normal map image."""

    def __call__(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            input_images: Input images
        Returns:
            Merged output image
        """
        x_image = validate_image(input_images[0], self.inputs()["x"])
        y_image = validate_image(input_images[1], self.inputs()["y"])
        z_image = validate_image(input_images[2], self.inputs()["z"])

        x_array = np.clip(np.array(x_image, float) - 128, -128, 127)
        y_array = np.clip(np.array(y_image, float) - 128, -128, 127)
        z_array = np.clip(np.array(z_image, float) / 2, 0, 127)
        magnitude = np.sqrt(x_array**2 + y_array**2 + z_array**2)
        x_array = np.clip(((x_array / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        y_array = np.clip(((y_array / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        z_array = np.clip(((z_array / magnitude) * 128) + 128, 0, 255).astype(np.uint8)
        output_array = np.zeros((*x_array.shape, 3), np.uint8)
        output_array[:, :, 0] = x_array
        output_array[:, :, 1] = y_array
        output_array[:, :, 2] = z_array
        output_image = Image.fromarray(output_array)

        return output_image

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
