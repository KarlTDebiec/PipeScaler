#!/usr/bin/env python
#   pipescaler/processors/image/mode_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Converts mode of image."""
from __future__ import annotations

from typing import Any

from PIL import Image, ImageColor

from pipescaler.common import validate_str
from pipescaler.core import ImageProcessor


class ModeProcessor(ImageProcessor):
    """Converts mode of image."""

    def __init__(
        self,
        mode: str = "RGB",
        background_color: str = "#000000",
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            mode: Output mode
            background_color: Background color of image
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.mode = validate_str(mode, self.supported_input_modes)
        self.background_color = ImageColor.getrgb(background_color)  # TODO: Validate

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Process an image

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        if input_image.mode == self.mode:
            output_image = input_image
        else:
            output_image = Image.new("RGBA", input_image.size, self.background_color)
            output_image.paste(input_image)
            if self.mode != "RGBA":
                output_image = output_image.convert(self.mode)

        return output_image
