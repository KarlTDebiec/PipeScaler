#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Splits image with transparency into separate alpha and color images."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

from pipescaler.common import ArgumentConflictError
from pipescaler.image.core import AlphaMode, MaskFillMode
from pipescaler.image.core.functions import is_monochrome
from pipescaler.image.core.operators import ImageSplitter
from pipescaler.image.core.validation import validate_image
from pipescaler.image.utilities import MaskFiller

if TYPE_CHECKING:
    from pipescaler.image.core.typing import ImageMode


class AlphaSplitter(ImageSplitter):
    """Splits image with transparency into separate color and alpha images."""

    def __init__(
        self,
        alpha_mode: AlphaMode = AlphaMode.GRAYSCALE,
        mask_fill_mode: MaskFillMode | None = None,
    ):
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
        input_img = validate_image(input_image, self.inputs()["input"])

        input_arr = np.array(input_img)

        color_arr = np.squeeze(input_arr[:, :, :-1])
        alpha_arr = input_arr[:, :, -1]
        color_img = Image.fromarray(color_arr)
        alpha_img = Image.fromarray(alpha_arr)

        if self.alpha_mode == AlphaMode.MONOCHROME_OR_GRAYSCALE:
            if is_monochrome(alpha_img):
                alpha_img = alpha_img.convert("1")
        if self.mask_fill_mode and alpha_img.mode == "1":
            color_img = MaskFiller.run(
                color_img,
                Image.fromarray(~np.array(alpha_img)),
                self.mask_fill_mode,
            )

        return color_img, alpha_img

    def __repr__(self) -> str:
        """Representation."""
        alpha_mode = repr(self.alpha_mode)
        if isinstance(self.alpha_mode, AlphaMode):
            alpha_mode = f"AlphaMode.{self.alpha_mode.name}"
        mask_fill_mode = repr(self.mask_fill_mode)
        if isinstance(self.mask_fill_mode, MaskFillMode):
            mask_fill_mode = f"MaskFillMode.{self.mask_fill_mode.name}"
        return (
            f"{self.__class__.__name__}("
            f"alpha_mode={alpha_mode}, "
            f"mask_fill_mode={mask_fill_mode})"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("LA", "RGBA"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "color": ("L", "RGB"),
            "alpha": ("1", "L"),
        }
