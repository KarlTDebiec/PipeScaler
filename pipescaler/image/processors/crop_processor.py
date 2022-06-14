#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Crops image canvas."""
from __future__ import annotations

from typing import Any

from PIL import Image

from pipescaler.common import validate_ints
from pipescaler.core.image import Processor, crop_image
from pipescaler.core.validation import validate_mode


class CropProcessor(Processor):
    """Crops image canvas."""

    def __init__(self, pixels: tuple[int, int, int, int], **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.left, self.top, self.right, self.bottom = validate_ints(
            pixels, length=4, min_value=0
        )

    def __call__(self, input_image: Image.Image) -> Image.Image:
        input_image, _ = validate_mode(input_image, self.inputs["input"])
        if (
            input_image.size[0] < self.left + self.right + 1
            or input_image.size[1] < self.top + self.bottom + 1
        ):
            raise ValueError()

        output_image = crop_image(
            input_image, self.left, self.top, self.right, self.bottom
        )

        return output_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "input": ("1", "L", "LA", "RGB", "RGBA"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "output": ("1", "L", "LA", "RGB", "RGBA"),
        }
