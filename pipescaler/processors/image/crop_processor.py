#!/usr/bin/env python
#   pipescaler/processors/image/crop_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Crops image canvas"""
from __future__ import annotations

from typing import Any

from PIL import Image

from pipescaler.common import validate_ints
from pipescaler.core import ImageProcessor, crop_image


class CropProcessor(ImageProcessor):
    """Crops image canvas"""

    def __init__(self, pixels: tuple[int], **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            pixels: Number of pixels to remove from left, top, right, and bottom
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.left, self.top, self.right, self.bottom = validate_ints(
            pixels, length=4, min_value=0
        )

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Process an image

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        if (
            input_image.size[0] < self.left + self.right + 1
            or input_image.size[1] < self.top + self.bottom + 1
        ):
            raise ValueError()

        output_image = crop_image(
            input_image, self.left, self.top, self.right, self.bottom
        )

        return output_image
