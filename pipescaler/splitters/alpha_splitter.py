#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Splits image with transparency into separate alpha and color images."""
from __future__ import annotations

from typing import Any, Optional, Union

import numpy as np
from PIL import Image

from pipescaler.common import ArgumentConflictError, validate_enum
from pipescaler.core import AlphaMode, MaskFillMode, is_monochrome, validate_mode
from pipescaler.core.stages import Splitter
from pipescaler.utilities import MaskFiller


class AlphaSplitter(Splitter):
    """Splits image with transparency into separate alpha and color images."""

    def __init__(
        self,
        alpha_mode: Union[type(AlphaMode), str] = AlphaMode.GRAYSCALE,
        mask_fill_mode: Optional[Union[type(MaskFillMode), str]] = None,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Args:
            alpha_mode: Mode of alpha channel handling to perform
            mask_fill_mode: Mode of mask filling to perform
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.alpha_mode = validate_enum(alpha_mode, AlphaMode)
        self.mask_fill_mode = None
        if mask_fill_mode is not None:
            if self.alpha_mode == AlphaMode.GRAYSCALE:
                raise ArgumentConflictError()
            self.mask_fill_mode = validate_enum(mask_fill_mode, MaskFillMode)
            self.mask_filler = MaskFiller(mask_fill_mode=self.mask_fill_mode)

    def __call__(
        self, *input_images: Union[Image.Image, tuple[Image.Image, ...]]
    ) -> Union[Image.Image, tuple[Image.Image, ...]]:
        input_image, _ = validate_mode(input_images[0], self.inputs["input"])

        input_array = np.array(input_image)
        color_array = np.squeeze(input_array[:, :, :-1])
        alpha_array = input_array[:, :, -1]

        color_image = Image.fromarray(color_array)
        alpha_image = Image.fromarray(alpha_array)

        if self.alpha_mode == AlphaMode.MONOCHROME_OR_GRAYSCALE:
            if is_monochrome(alpha_image):
                alpha_image = alpha_image.convert("1")
        if self.mask_fill_mode is not None and alpha_image.mode == "1":
            color_image = self.mask_filler.fill(color_image, alpha_image)

        return color_image, alpha_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "input": ("LA", "RGBA"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "color": ("L", "RGB"),
            "alpha": ("1", "L"),
        }
