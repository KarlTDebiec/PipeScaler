#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Converts image to black and white using threshold, optionally denoising."""
from __future__ import annotations

from typing import no_type_check

import numpy as np
from core.stages import Processor
from numba import njit
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import validate_mode


class ThresholdProcessor(Processor):
    """Converts image to black and white using threshold, optionally denoising."""

    def __init__(self, threshold: int = 128, denoise: bool = False) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            threshold: Threshold differentiating black and white
            denoise: Flip color of pixels bordered by less than 5 pixels of the same
              color
        """
        self.threshold = validate_int(threshold, 1, 244)
        self.denoise = denoise

    def __call__(self, input_image: Image.Image) -> Image.Image:
        input_image, input_mode = validate_mode(input_image, self.inputs["input"])

        if input_mode == "L":
            output_image = input_image.point(lambda p: p > self.threshold and 255)
        else:
            output_image = input_image
        if self.denoise:
            output_data = np.array(output_image)
            self.denoise_data(output_data)
            output_image = Image.fromarray(output_data)

        return output_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "input": ("1", "L"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "output": ("1",),
        }

    @no_type_check
    @staticmethod
    @njit(nogil=True, cache=True, fastmath=True)
    def denoise_data(data: np.ndarray) -> None:
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
                else:
                    if (slc == 255).sum() < 4:
                        data[y, x] = 0
