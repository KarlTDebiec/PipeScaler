#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Splits a normal map image into separate x, y, and z images."""

from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.image.core.operators import ImageSplitter
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image


class NormalSplitter(ImageSplitter):
    """Splits a normal map image into separate x, y, and z images."""

    def __call__(self, input_img: Image.Image) -> tuple[Image.Image, ...]:
        """Split an image.

        Arguments:
            input_img: Input image
        Returns:
            Split output images
        """
        input_img = validate_image(input_img, self.inputs()["input"])
        input_arr = np.array(input_img)
        x_arr = input_arr[:, :, 0]
        y_arr = input_arr[:, :, 1]
        z_arr = (input_arr[:, :, 2].astype(float) - 128) * 2
        z_arr = np.clip(z_arr, 0, 255).astype(np.uint8)

        x_img = Image.fromarray(x_arr)
        y_img = Image.fromarray(y_arr)
        z_img = Image.fromarray(z_arr)

        return x_img, y_img, z_img

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("RGB",),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "x": ("L",),
            "y": ("L",),
            "z": ("L",),
        }
