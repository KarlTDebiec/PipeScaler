#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Resizes image canvas."""
from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.common import validate_float, validate_str
from pipescaler.core.image import Processor


class ResizeProcessor(Processor):
    """Resizes image canvas."""

    resample_methods = {
        "bicubic": Image.BICUBIC,
        "bilinear": Image.BILINEAR,
        "lanczos": Image.LANCZOS,
        "nearest": Image.NEAREST,
    }

    def __init__(self, scale: float, resample: str = "lanczos") -> None:
        """Validate and store configuration and initialize.

        Arguments:
            scale: Output image scale relative to input image
            resample: Resample algorithm
        """
        self.scale = validate_float(scale, min_value=0)
        self.resample = self.resample_methods[
            validate_str(resample, options=self.resample_methods.keys())
        ]

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Args:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_array = np.array(input_image)

        size = (
            round(input_image.size[0] * self.scale),
            round(input_image.size[1] * self.scale),
        )
        if input_image.mode == "RGBA":
            rgba_array = np.zeros((size[1], size[0], 4), np.uint8)
            rgb_image = Image.fromarray(input_array[:, :, :3])
            rgb_image = rgb_image.resize(size, resample=self.resample)
            rgba_array[:, :, :3] = np.array(rgb_image)
            a_image = Image.fromarray(input_array[:, :, 3])
            a_image = a_image.resize(size, resample=self.resample)
            rgba_array[:, :, 3] = np.array(a_image)
            output_image = Image.fromarray(rgba_array)
        elif input_image.mode == "LA":
            la_array = np.zeros((size[1], size[0], 2), np.uint8)
            l_image = Image.fromarray(input_array[:, :, 0])
            l_image = l_image.resize(size, resample=self.resample)
            la_array[:, :, 0] = np.array(l_image)
            a_image = Image.fromarray(input_array[:, :, 1])
            a_image = a_image.resize(size, resample=self.resample)
            la_array[:, :, 1] = np.array(a_image)
            output_image = Image.fromarray(la_array)
        else:
            output_image = input_image.resize(size, resample=self.resample)

        return output_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L", "LA", "RGB", "RGBA"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1", "L", "LA", "RGB", "RGBA"),
        }
