#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Resizes image canvas."""

from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.common.validation import val_float, val_str
from pipescaler.image.core.operators import ImageProcessor


class ResizeProcessor(ImageProcessor):
    """Resizes image canvas."""

    resample_methods = {
        "bicubic": Image.Resampling.BICUBIC,  # type: ignore
        "bilinear": Image.Resampling.BILINEAR,  # type: ignore
        "lanczos": Image.Resampling.LANCZOS,  # type: ignore
        "nearest": Image.Resampling.NEAREST,  # type: ignore
    }

    def __init__(self, scale: float, resample: str = "lanczos"):
        """Validate and store configuration and initialize.

        Arguments:
            scale: Output image scale relative to input image
            resample: Resample algorithm
        """
        super().__init__()

        self.scale = val_float(scale, min_value=0)
        self.resample = self.resample_methods[
            val_str(resample, options=self.resample_methods.keys())
        ]

    def __call__(self, input_img: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_img: Input image
        Returns:
            Processed output image
        """
        input_arr = np.array(input_img)

        size = (
            round(input_img.size[0] * self.scale),
            round(input_img.size[1] * self.scale),
        )
        if input_img.mode == "RGBA":
            rgba_arr = np.zeros((size[1], size[0], 4), np.uint8)
            rgb_img = Image.fromarray(input_arr[:, :, :3])
            rgb_img = rgb_img.resize(size, resample=self.resample)
            rgba_arr[:, :, :3] = np.array(rgb_img)
            a_img = Image.fromarray(input_arr[:, :, 3])
            a_img = a_img.resize(size, resample=self.resample)
            rgba_arr[:, :, 3] = np.array(a_img)
            output_img = Image.fromarray(rgba_arr)
        elif input_img.mode == "LA":
            la_arr = np.zeros((size[1], size[0], 2), np.uint8)
            l_img = Image.fromarray(input_arr[:, :, 0])
            l_img = l_img.resize(size, resample=self.resample)
            la_arr[:, :, 0] = np.array(l_img)
            a_img = Image.fromarray(input_arr[:, :, 1])
            a_img = a_img.resize(size, resample=self.resample)
            la_arr[:, :, 1] = np.array(a_img)
            output_img = Image.fromarray(la_arr)
        else:
            output_img = input_img.resize(size, resample=self.resample)

        return output_img

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"scale={self.scale!r}, "
            f"resample={self.resample!r})"
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L", "LA", "RGB", "RGBA"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1", "L", "LA", "RGB", "RGBA"),
        }
