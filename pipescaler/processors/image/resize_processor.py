#!/usr/bin/env python
#   pipescaler/processors/image/resize_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Resizes image canvas."""
from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image

from pipescaler.common import validate_float, validate_str
from pipescaler.core import ImageProcessor


class ResizeProcessor(ImageProcessor):
    """Resizes image canvas."""

    resample_methods = {
        "bicubic": Image.BICUBIC,
        "bilinear": Image.BILINEAR,
        "lanczos": Image.LANCZOS,
        "nearest": Image.NEAREST,
    }

    def __init__(self, scale: float, resample: str = "lanczos", **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            scale: Output image scale relative to input image
            resample: Resample algorithm
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_float(scale, min_value=0)
        self.resample = self.resample_methods[
            validate_str(resample, options=self.resample_methods.keys())
        ]

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Process an image

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        # noinspection PyTypeChecker
        input_datum = np.array(input_image)

        # Process image
        size = (
            round(input_image.size[0] * self.scale),
            round(input_image.size[1] * self.scale),
        )
        if input_image.mode == "RGBA":
            rgba_datum = np.zeros((size[1], size[0], 4), np.uint8)
            rgb_image = Image.fromarray(input_datum[:, :, :3])
            rgb_image = rgb_image.resize(size, resample=self.resample)
            # noinspection PyTypeChecker
            rgba_datum[:, :, :3] = np.array(rgb_image)
            a_image = Image.fromarray(input_datum[:, :, 3])
            a_image = a_image.resize(size, resample=self.resample)
            # noinspection PyTypeChecker
            rgba_datum[:, :, 3] = np.array(a_image)
            output_image = Image.fromarray(rgba_datum)
        elif input_image.mode == "LA":
            la_datum = np.zeros((size[1], size[0], 2), np.uint8)
            l_image = Image.fromarray(input_datum[:, :, 0])
            l_image = l_image.resize(size, resample=self.resample)
            # noinspection PyTypeChecker
            la_datum[:, :, 0] = np.array(l_image)
            a_image = Image.fromarray(input_datum[:, :, 1])
            a_image = a_image.resize(size, resample=self.resample)
            # noinspection PyTypeChecker
            la_datum[:, :, 1] = np.array(a_image)
            output_image = Image.fromarray(la_datum)
        else:
            output_image = input_image.resize(size, resample=self.resample)

        return output_image
