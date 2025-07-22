#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Converts image to black and white using threshold, optionally denoising."""

from __future__ import annotations

from typing import no_type_check

import numpy as np
from numba import njit
from PIL import Image

from pipescaler.common.validation import val_int
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image_and_convert_mode


class ThresholdProcessor(ImageProcessor):
    """Converts image to black and white using threshold, optionally denoising."""

    def __init__(self, threshold: int = 128, denoise: bool = False) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            threshold: Threshold differentiating black and white
            denoise: Flip color of pixels bordered by less than 5 pixels of the same
              color
        """
        super().__init__()

        self.threshold = val_int(threshold, min_value=1, max_value=244)
        self.denoise = denoise

    def __call__(self, input_img: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_img: Input image
        Returns:
            Processed output image
        """
        input_img, input_mode = validate_image_and_convert_mode(
            input_img, self.inputs()["input"]
        )

        if input_mode == "L":
            output_img = input_img.point(lambda p: p > self.threshold and 255)
        else:
            output_img = input_img
        if self.denoise:
            output_arr = np.array(output_img)
            self.denoise_array(output_arr)
            output_img = Image.fromarray(output_arr)

        return output_img

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"threshold={self.threshold!r},"
            f"denoise={self.denoise!r})"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1",),
        }

    @no_type_check
    @staticmethod
    @njit(nogil=True, cache=True, fastmath=True)
    def denoise_array(data: np.ndarray) -> None:
        """Flip color of pixels bordered by less than 5 pixels of the same color.

        Arguments:
            data: Input image array; modified in-place
        """
        for x in range(1, data.shape[1] - 1):
            for y in range(1, data.shape[0] - 1):
                slc = data[y - 1 : y + 2, x - 1 : x + 2]
                if data[y, x] == 0:
                    if (slc == 0).sum() < 4:
                        data[y, x] = 255
                elif (slc == 255).sum() < 4:
                    data[y, x] = 0
