#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Crops image canvas."""
from __future__ import annotations

from PIL import Image

from pipescaler.common import validate_ints
from pipescaler.core.image import Processor, crop_image, validate_image


class CropProcessor(Processor):
    """Crops image canvas."""

    def __init__(self, pixels: tuple[int, int, int, int]) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            pixels: Pixels to crop from left, top, right, and bottom
        """
        self.left, self.top, self.right, self.bottom = validate_ints(
            pixels, length=4, min_value=0
        )

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image = validate_image(input_image, self.inputs()["input"])
        if (
            input_image.size[0] < self.left + self.right + 1
            or input_image.size[1] < self.top + self.bottom + 1
        ):
            raise ValueError("Image is too small to crop by provided pixels")

        output_image = crop_image(
            input_image, self.left, self.top, self.right, self.bottom
        )

        return output_image

    def __repr__(self):
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"pixels={(self.left,self.top,self.right,self.bottom)})"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L", "LA", "RGB", "RGBA"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1", "L", "LA", "RGB", "RGBA"),
        }
