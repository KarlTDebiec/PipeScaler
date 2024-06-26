#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sharpens an image."""
from __future__ import annotations

import numpy as np
from PIL import Image
from scipy.signal import convolve2d

from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.validation import validate_image


class SharpenProcessor(ImageProcessor):
    """Sharpens an image."""

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], float)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image = validate_image(input_image, self.inputs()["input"])

        if input_image.mode == "L":
            input_array = np.array(input_image).astype(float)
            output_array = convolve2d(input_array, self.kernel, "same")
            output_array = np.clip(output_array, 0, 255).astype(np.uint8)
            output_image = Image.fromarray(output_array)
        else:
            hsv_image = input_image.convert("HSV")

            hsv_array = np.array(hsv_image)
            v_array = hsv_array[:, :, 2].astype(float)
            v_array = convolve2d(v_array, self.kernel, "same")
            hsv_array[:, :, 2] = np.clip(v_array, 0, 255).astype(np.uint8)
            output_image = Image.fromarray(hsv_array, mode="HSV").convert("RGB")

        return output_image

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("L", "RGB"),
        }
