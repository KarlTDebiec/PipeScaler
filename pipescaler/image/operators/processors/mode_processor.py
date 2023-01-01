#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Converts mode of image."""
from __future__ import annotations

from PIL import Image, ImageColor

from pipescaler.common import validate_str
from pipescaler.image.core import validate_image
from pipescaler.image.core.operators import ImageProcessor


class ModeProcessor(ImageProcessor):
    """Converts mode of image."""

    def __init__(self, mode: str = "RGB", background_color: str = "#000000") -> None:
        """Validate and store configuration and initialize.

        Arguments:
            mode: Output mode
            background_color: Background color
        """
        self.mode = validate_str(mode, self.outputs()["output"])
        self.background_color = ImageColor.getrgb(background_color)  # TODO: Validate

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image = validate_image(input_image, self.inputs()["input"])

        if input_image.mode == self.mode:
            return input_image

        output_image = Image.new("RGBA", input_image.size, self.background_color)
        output_image.paste(input_image)
        if self.mode != "RGBA":
            output_image = output_image.convert(self.mode)

        return output_image

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"mode={self.mode!r}, "
            f"background_color={self.background_color!r})"
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
