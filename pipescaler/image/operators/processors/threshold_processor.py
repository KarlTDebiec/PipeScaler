#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
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

__all__ = ["ThresholdProcessor"]


class ThresholdProcessor(ImageProcessor):
    """Threshold and optionally denoise black-and-white pixels.

    Mode `1` inputs retain mode `1`; mode `L` inputs retain mode `L` with
    pixel values restricted to 0 and 255. Palette inputs are expanded before
    validating their mode.
    """

    def __init__(self, threshold: int = 128, denoise: bool = False):
        """Validate and store configuration and initialize.

        Arguments:
            threshold: threshold differentiating black and white
            denoise: flip color of pixels bordered by less than 5 pixels of the same
              color
        """
        super().__init__()

        self.threshold = val_int(threshold, min_value=1, max_value=244)
        self.denoise = denoise

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: input image
        Returns:
            black-and-white image retaining the validated input mode
        """
        input_image, input_mode = validate_image_and_convert_mode(
            input_image, self.inputs()["input"]
        )

        if input_mode == "L":
            output_img = input_image.point(lambda p: p > self.threshold and 255)
        else:
            output_img = input_image
        if self.denoise:
            output_arr = np.array(output_img)
            self.denoise_array(output_arr)
            output_img = Image.fromarray(output_arr)

        return output_img

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        return (
            f"{self.__class__.__name__}("
            f"threshold={self.threshold!r},"
            f"denoise={self.denoise!r})"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator.

        Returns:
            mapping of input names to their supported image modes
        """
        return {
            "input": ("1", "L"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator.

        Returns:
            mapping of output names to their supported image modes
        """
        return {
            "output": ("1", "L"),
        }

    @no_type_check
    @staticmethod
    @njit(nogil=True, cache=True, fastmath=True)
    def denoise_array(data: np.ndarray):
        """Flip color of pixels bordered by less than 5 pixels of the same color.

        Arguments:
            data: input image array; modified in-place
        """
        for x in range(1, data.shape[1] - 1):
            for y in range(1, data.shape[0] - 1):
                slc = data[y - 1 : y + 2, x - 1 : x + 2]
                if data[y, x] == 0:
                    if (slc == 0).sum() < 4:
                        data[y, x] = 255
                elif (slc != 0).sum() < 4:
                    data[y, x] = 0
