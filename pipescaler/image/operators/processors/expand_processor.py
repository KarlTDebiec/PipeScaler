#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Expands image canvas by mirroring image around edges."""

from __future__ import annotations

from PIL import Image

from pipescaler.common.validation import val_int
from pipescaler.image.core.functions import expand_image
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image


class ExpandProcessor(ImageProcessor):
    """Expands image canvas by mirroring image around edges."""

    def __init__(self, pixels: tuple[int, int, int, int]):
        """Validate and store configuration and initialize.

        Arguments:
            pixels: Pixels to add to left, top, right, and bottom
        """
        super().__init__()

        self.left, self.top, self.right, self.bottom = val_int(
            pixels, n_values=4, min_value=0
        )

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image = validate_image(input_image, self.inputs()["input"])

        output_image = expand_image(
            input_image, self.left, self.top, self.right, self.bottom
        )

        return output_image

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"pixels=({self.left!r}, {self.top!r}, {self.right!r}, {self.bottom!r}))"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L", "LA", "RGB", "RGBA"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1", "L", "LA", "RGB", "RGBA"),
        }
