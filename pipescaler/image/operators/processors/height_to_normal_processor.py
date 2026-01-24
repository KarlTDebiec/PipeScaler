#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Converts height map image to a normal map image."""

from __future__ import annotations

from PIL import Image

from pipescaler.common.validation import val_float
from pipescaler.image.core.functions import (
    generate_normal_map_from_height_map_image,
    smooth_image,
)
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.typing import ImageMode
from pipescaler.image.core.validation import validate_image


class HeightToNormalProcessor(ImageProcessor):
    """Converts height map image to a normal map image."""

    def __init__(self, sigma: float | None = None):
        """Validate and store configuration and initialize.

        Arguments:
            sigma: Gaussian smoothing to apply to image
        """
        super().__init__()

        self.sigma = val_float(sigma, min_value=0) if sigma else None

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image = validate_image(input_image, self.inputs()["input"])

        if self.sigma:
            input_image = smooth_image(input_image, self.sigma)
        output_image = generate_normal_map_from_height_map_image(input_image)

        return output_image

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(sigma={self.sigma!r})"

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("L",),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("RGB",),
        }
