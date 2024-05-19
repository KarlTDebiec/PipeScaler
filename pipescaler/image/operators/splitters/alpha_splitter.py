#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Splits image with transparency into separate alpha and color images."""
from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.common import ArgumentConflictError
from pipescaler.image.core import AlphaMode, MaskFillMode
from pipescaler.image.core.functions import is_monochrome
from pipescaler.image.core.operators import ImageSplitter
from pipescaler.image.core.validation import validate_image
from pipescaler.image.utilities import MaskFiller


class AlphaSplitter(ImageSplitter):
    """Splits image with transparency into separate color and alpha images."""

    def __init__(
        self,
        alpha_mode: AlphaMode = AlphaMode.GRAYSCALE,
        mask_fill_mode: MaskFillMode | None = None,
    ) -> None:
        """Validate configuration and initialize.

        Arguments:
            alpha_mode: Mode of alpha treatment to perform
            mask_fill_mode: Mode of mask filling to perform
        """
        super().__init__()

        self.alpha_mode = alpha_mode
        self.mask_fill_mode = None
        if mask_fill_mode:
            if self.alpha_mode == AlphaMode.GRAYSCALE:
                raise ArgumentConflictError(
                    "Mask filling is only supported for "
                    "alpha_mode MONOCHROME_OR_GRAYSCALE"
                )
            self.mask_fill_mode = mask_fill_mode

    def __call__(self, input_image: Image.Image) -> tuple[Image.Image, ...]:
        """Split an image.

        Arguments:
            input_image: Input image
        Returns:
            Split output images
        """
        input_image = validate_image(input_image, self.inputs()["input"])

        input_array = np.array(input_image)

        color_array = np.squeeze(input_array[:, :, :-1])
        alpha_array = input_array[:, :, -1]
        color_image = Image.fromarray(color_array)
        alpha_image = Image.fromarray(alpha_array)

        if self.alpha_mode == AlphaMode.MONOCHROME_OR_GRAYSCALE:
            if is_monochrome(alpha_image):
                alpha_image = alpha_image.convert("1")
        if self.mask_fill_mode and alpha_image.mode == "1":
            color_image = MaskFiller.run(
                color_image,
                Image.fromarray(~np.array(alpha_image)),
                self.mask_fill_mode,
            )

        return color_image, alpha_image

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"alpha_mode={self.alpha_mode!r}, "
            f"mask_fill_mode={self.mask_fill_mode!r})"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("LA", "RGBA"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "color": ("L", "RGB"),
            "alpha": ("1", "L"),
        }
