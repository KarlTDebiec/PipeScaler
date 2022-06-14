#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Expands image canvas by mirroring image around edges."""
from __future__ import annotations

from PIL import Image

from pipescaler.common import validate_ints
from pipescaler.core.image import Processor, expand_image
from pipescaler.core.validation import validate_mode


class ExpandProcessor(Processor):
    """Expands image canvas by mirroring image around edges."""

    def __init__(self, pixels: tuple[int, int, int, int]) -> None:
        self.left, self.top, self.right, self.bottom = validate_ints(
            pixels, length=4, min_value=0
        )

    def __call__(self, input_image: Image.Image) -> Image.Image:
        input_image, _ = validate_mode(input_image, self.inputs["input"])

        output_image = expand_image(
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
