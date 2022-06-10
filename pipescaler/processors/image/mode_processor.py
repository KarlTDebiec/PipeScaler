#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Converts mode of image."""
from __future__ import annotations

from PIL import Image, ImageColor

from pipescaler.common import validate_str
from pipescaler.core import validate_mode
from pipescaler.core.stages import Processor


class ModeProcessor(Processor):
    """Converts mode of image."""

    def __init__(
        self,
        mode: str = "RGB",
        background_color: str = "#000000",
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            mode: Output mode
            background_color: Background color of image
        """
        self.mode = validate_str(mode, self.outputs["output"])
        self.background_color = ImageColor.getrgb(background_color)  # TODO: Validate

    def __call__(self, input_image: Image.Image) -> Image.Image:
        input_image, input_mode = validate_mode(input_image, self.inputs["input"])

        if input_image.mode == self.mode:
            output_image = input_image
        else:
            output_image = Image.new("RGBA", input_image.size, self.background_color)
            output_image.paste(input_image)
            if self.mode != "RGBA":
                output_image = output_image.convert(self.mode)

        return output_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "input": ("1", "L", "LA", "RGB", "RGBA"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "output": ("1", "L", "LA", "RGB", "RGBA"),
        }
