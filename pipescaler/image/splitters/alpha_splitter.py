#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Splits image with transparency into separate alpha and color images."""
from __future__ import annotations

from typing import Optional, Union

import numpy as np
from PIL import Image

from pipescaler.common import ArgumentConflictError, validate_enum
from pipescaler.core.enums import AlphaMode, MaskFillMode
from pipescaler.core.image import Splitter, is_monochrome
from pipescaler.core.validation import validate_image
from pipescaler.utilities import MaskFiller


class AlphaSplitter(Splitter):
    """Splits image with transparency into separate color and alpha images."""

    def __init__(
        self,
        alpha_mode: Union[AlphaMode, str] = AlphaMode.GRAYSCALE,
        mask_fill_mode: Optional[Union[MaskFillMode, str]] = None,
    ) -> None:
        """Validate configuration and initialize.

        Arguments:
            alpha_mode: Mode of alpha treatment to perform
            mask_fill_mode: Mode of mask filling to perform
        """
        self.alpha_mode = validate_enum(alpha_mode, AlphaMode)
        self.mask_fill_mode = None
        if mask_fill_mode is not None:
            if self.alpha_mode == AlphaMode.GRAYSCALE:
                raise ArgumentConflictError(
                    "Mask filling is only supported for "
                    "alpha_mode MONOCHROME_OR_GRAYSCALE"
                )
            self.mask_fill_mode = validate_enum(mask_fill_mode, MaskFillMode)
            self.mask_filler = MaskFiller(mask_fill_mode=self.mask_fill_mode)

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
        if self.mask_fill_mode is not None and alpha_image.mode == "1":
            color_image = self.mask_filler.fill(
                color_image, Image.fromarray(~np.array(alpha_image))
            )

        return color_image, alpha_image

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
