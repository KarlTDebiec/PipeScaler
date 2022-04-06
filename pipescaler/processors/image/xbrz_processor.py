#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Upscales image using xbrz."""
from __future__ import annotations

from typing import Any

import numpy as np
import xbrz
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import convert_mode
from pipescaler.core.stages.processors import ImageProcessor


class XbrzProcessor(ImageProcessor):
    """Upscales image using xbrz.

    See [xbrz](https://github.com/ioistired/xbrz.py)."""

    def __init__(self, scale: int = 4, **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            scale: Factor by which to scale output image relative to input
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_int(scale, 2, 6)

    def process(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        input_image, input_mode = convert_mode(input_image, "RGBA")

        output_image = xbrz.scale_pillow(input_image, self.scale)
        if input_mode == "RGB":
            output_image = Image.fromarray(np.array(output_image)[:, :, :3])
        elif input_mode == "LA":
            output_image = output_image.convert("LA")
        elif input_mode in ("1", "L"):
            output_image = Image.fromarray(np.array(output_image)[:, :, :3]).convert(
                "L"
            )

        return output_image

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return "Upscales image using [xbrz](https://github.com/ioistired/xbrz.py)."
