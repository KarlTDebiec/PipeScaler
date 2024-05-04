#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Upscales image using xbrz."""
from __future__ import annotations

import numpy as np
import xbrz
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.image.core import validate_image_and_convert_mode
from pipescaler.image.core.operators import ImageProcessor


class XbrzProcessor(ImageProcessor):
    """Upscales image using xbrz.

    See [xbrz](https://github.com/ioistired/xbrz.py).
    """

    def __init__(self, scale: int = 4) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            scale: Factor by which to scale output image relative to input
        """
        super().__init__()

        self.scale = validate_int(scale, 2, 6)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image, output_mode = validate_image_and_convert_mode(
            input_image, self.inputs()["input"], "RGBA"
        )

        output_image: Image.Image = xbrz.scale_pillow(input_image, self.scale)
        if output_mode == "RGB":
            output_image = Image.fromarray(np.array(output_image)[:, :, :3])
        elif output_mode == "LA":
            output_image = output_image.convert("LA")
        elif output_mode in ("1", "L"):
            output_image = Image.fromarray(np.array(output_image)[:, :, :3]).convert(
                "L"
            )

        return output_image

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(scale={self.scale!r})"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return "Upscales image using [xbrz](https://github.com/ioistired/xbrz.py)."

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
