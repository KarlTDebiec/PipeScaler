#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Converts mode of image."""

from __future__ import annotations

from PIL import Image, ImageColor

from pipescaler.common.validation import val_str
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image


class ModeProcessor(ImageProcessor):
    """Converts mode of image."""

    def __init__(
        self,
        mode: str = "RGB",
        background_color: str = "#000000",
        threshold: int = 128,
    ):
        """Validate and store configuration and initialize.

        Arguments:
            mode: Output mode
            background_color: Background color
            threshold: Threshold for binary conversion (only used for mode '1')
        """
        super().__init__()

        self.mode = val_str(mode, self.outputs()["output"])
        self.background_color = ImageColor.getrgb(background_color)
        self.threshold = threshold

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

        if self.mode == "1":
            if input_image.mode in ("LA", "RGB", "RGBA"):
                input_image = input_image.convert("L")
            return input_image.point(lambda x: 0 if x < self.threshold else 255, "1")

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
            f"background_color={self.background_color!r}, "
            f"threshold={self.threshold!r})"
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
