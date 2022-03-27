#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Converts image to black and white using threshold, optionally denoising."""
from __future__ import annotations

from typing import Any, List, no_type_check

import numba as nb
import numpy as np
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import ImageProcessor


class ThresholdProcessor(ImageProcessor):
    """Converts image to black and white using threshold, optionally denoising."""

    def __init__(
        self, threshold: int = 128, denoise: bool = False, **kwargs: Any
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            threshold: Threshold differentiating black and white
            denoise: Flip color of pixels bordered by less than 5 pixels of the same
              color
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.threshold = validate_int(threshold, 1, 244)
        self.denoise = denoise

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Process an image

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        output_image = input_image.point(lambda p: p > self.threshold and 255)
        if self.denoise:
            # noinspection PyTypeChecker
            output_data = np.array(output_image)
            self.denoise_data(output_data)
            output_image = Image.fromarray(output_data)

        return output_image

    @classmethod
    @property
    def supported_input_modes(self) -> List[str]:
        """Supported modes for input image"""
        return ["L"]

    @no_type_check
    @staticmethod
    @nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
    def denoise_data(data: np.ndarray) -> None:
        """
        Flip color of pixels bordered by less than 5 pixels of the same color

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
