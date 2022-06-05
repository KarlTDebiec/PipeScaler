#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Merges alpha and color images into a single image with transparency."""
from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.core.stages import Merger


class AlphaMerger(Merger):
    """Merges alpha and color images into a single image with transparency."""

    def __call__(self, *input_images: tuple[Image.Image, ...]) -> Image.Image:
        color_image, alpha_image = input_images
        # validate_image(color_image, ["L", "RGB"])
        # validate_image(alpha_image, ["1", "L"])

        color_array = np.array(color_image)
        if alpha_image.mode == "L":
            alpha_array = np.array(alpha_image)
        else:
            alpha_array = np.array(alpha_image.convert("L"))
        if color_image.mode == "L":
            output_array = np.zeros((*color_array.shape, 2), np.uint8)
            output_array[:, :, 0] = color_array
        else:
            output_array = np.zeros((*color_array.shape[:-1], 4), np.uint8)
            output_array[:, :, :-1] = color_array
        output_array[:, :, -1] = alpha_array
        output_image = Image.fromarray(output_array)

        return output_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "color": ("L", "RGB"),
            "alpha": ("1", "L"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "outlet": ("LA", "RGBA"),
        }
