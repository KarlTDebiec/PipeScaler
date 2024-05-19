#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sets entire image color to its average color, optionally resizing."""
from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.common.validation import validate_float
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.validation import validate_image_and_convert_mode


class SolidColorProcessor(ImageProcessor):
    """Sets entire image color to its average color, optionally resizing."""

    def __init__(self, scale: float = 1) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            scale: Scale of output image relative to input
        """
        super().__init__()

        self.scale = validate_float(scale)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image, output_mode = validate_image_and_convert_mode(
            input_image, self.inputs()["input"]
        )

        size = (
            round(input_image.size[0] * self.scale),
            round(input_image.size[1] * self.scale),
        )
        array = np.array(input_image)
        if input_image.mode in ("LA", "RGB", "RGBA"):
            color: int | tuple[int, int, int] = tuple(
                np.rint(array.mean(axis=(0, 1))).astype(np.uint8)  # type: ignore
            )
        elif input_image.mode == "L":
            color = round(array.mean())
        else:
            color = 255 if array.mean() >= 0.5 else 0
        output_image = Image.new(output_mode, size, color)

        return output_image

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(scale={self.scale!r})"

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
