#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sharpens an image."""

from __future__ import annotations

import numpy as np
from PIL import Image
from scipy.signal import convolve2d

from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image


class SharpenProcessor(ImageProcessor):
    """Sharpens an image."""

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], float)

    def __call__(self, input_img: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_img: Input image
        Returns:
            Processed output image
        """
        input_img = validate_image(input_img, self.inputs()["input"])

        if input_img.mode == "L":
            input_arr = np.array(input_img).astype(float)
            output_arr = convolve2d(input_arr, self.kernel, "same")
            output_arr = np.clip(output_arr, 0, 255).astype(np.uint8)
            output_img = Image.fromarray(output_arr)
        else:
            hsv_img = input_img.convert("HSV")

            hsv_arr = np.array(hsv_img)
            v_arr = hsv_arr[:, :, 2].astype(float)
            v_arr = convolve2d(v_arr, self.kernel, "same")
            hsv_arr[:, :, 2] = np.clip(v_arr, 0, 255).astype(np.uint8)
            output_img = Image.fromarray(hsv_arr, mode="HSV").convert("RGB")

        return output_img

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("L", "RGB"),
        }
