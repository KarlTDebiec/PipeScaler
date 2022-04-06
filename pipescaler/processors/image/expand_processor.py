#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Expands image canvas by mirroring image around edges."""
from __future__ import annotations

from typing import Any

from PIL import Image

from pipescaler.common import validate_ints
from pipescaler.core import expand_image
from pipescaler.core.stages.processors import ImageProcessor


class ExpandProcessor(ImageProcessor):
    """Expands image canvas by mirroring image around edges."""

    def __init__(self, pixels: tuple[int], **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            pixels: Number of pixels to add to left, top, right, and bottom
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
        output_image = expand_image(
            input_image, self.left, self.top, self.right, self.bottom
        )

        return output_image
