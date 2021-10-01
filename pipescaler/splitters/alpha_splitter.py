#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from logging import info
from typing import Any, Dict

import numpy as np
from PIL import Image

from pipescaler.core import Splitter, validate_image


class AlphaSplitter(Splitter):
    """Splits image with transparency into separate alpha and color images."""

    def __init__(self, smart_fill: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.smart_fill = smart_fill

    def __call__(self, infile: str, **kwargs: Any) -> Dict[str, str]:
        outfiles = {k: kwargs.get(k) for k in self.outlets}

        # Read image
        input_image = validate_image(infile, ["LA", "RGBA"])

        # Split image
        input_datum = np.array(input_image)
        color_datum = np.squeeze(input_datum[:, :, :-1])
        alpha_datum = input_datum[:, :, -1]
        if self.smart_fill:
            color_datum[alpha_datum == 0] = [255, 0, 255]
            while True:
                try:
                    color_datum = self.run_iter(color_datum, [255, 0, 255])
                except StopIteration:
                    break
        color_image = Image.fromarray(color_datum)
        alpha_image = Image.fromarray(alpha_datum)

        # Write images
        color_image.save(outfiles["color"])
        info(f"{self}: '{outfiles['color']}' saved")
        alpha_image.save(outfiles["alpha"])
        info(f"{self}: '{outfiles['alpha']}' saved")

        return outfiles

    @property
    def outlets(self):
        return ["color", "alpha"]

    @classmethod
    def run_iter(cls, color_datum: np.ndarray, alpha_color):

        # Identify transparent pixels in image
        transparent_pixels = (color_datum == alpha_color).all(axis=2)
        if transparent_pixels.sum() == 0:
            raise StopIteration

        # count the number of opaque pixels adjacent to each pixel in image
        adjacent_opaque_pixels = cls.adjacent_opaque_pixels(transparent_pixels)

        # Disregard the number of of adjacent opaque pixels for pixels that are themselves opaque
        adjacent_opaque_pixels[np.logical_not(transparent_pixels)] = 0

        # Identify pixels who have the max number of adjacent opaque pixels
        pixels_to_fill = np.logical_and(
            transparent_pixels, adjacent_opaque_pixels == adjacent_opaque_pixels.max(),
        )

        # Calculate the color of pixels to fill
        sum_of_adjacent_opaque_pixels = cls.sum_of_adjacent_opaque_pixels(
            color_datum, transparent_pixels
        )
        colors_of_pixels_to_fill = np.round(
            sum_of_adjacent_opaque_pixels[pixels_to_fill] / adjacent_opaque_pixels.max()
        ).astype(np.uint8)

        # Set colors and return
        color_datum[pixels_to_fill] = colors_of_pixels_to_fill
        return color_datum

    @staticmethod
    def adjacent_opaque_pixels(transparent_pixels):
        adjacent_opaque_pixels = np.zeros(transparent_pixels.shape, int)
        adjacent_opaque_pixels[:-1, :-1] += 1
        adjacent_opaque_pixels[:, :-1] += 1
        adjacent_opaque_pixels[1:, :-1] += 1
        adjacent_opaque_pixels[:-1, :] += 1
        adjacent_opaque_pixels[1:, :] += 1
        adjacent_opaque_pixels[:-1, 1:] += 1
        adjacent_opaque_pixels[:, 1:] += 1
        adjacent_opaque_pixels[1:, 1:] += 1

        adjacent_opaque_pixels[:-1, :-1] -= transparent_pixels[1:, 1:]
        adjacent_opaque_pixels[:, :-1] -= transparent_pixels[:, 1:]
        adjacent_opaque_pixels[1:, :-1] -= transparent_pixels[:-1, 1:]
        adjacent_opaque_pixels[:-1, :] -= transparent_pixels[1:, :]
        adjacent_opaque_pixels[1:, :] -= transparent_pixels[:-1, :]
        adjacent_opaque_pixels[:-1, 1:] -= transparent_pixels[1:, :-1]
        adjacent_opaque_pixels[:, 1:] -= transparent_pixels[:, :-1]
        adjacent_opaque_pixels[1:, 1:] -= transparent_pixels[:-1, :-1]

        return adjacent_opaque_pixels

    @staticmethod
    def sum_of_adjacent_opaque_pixels(color_datum, transparent_pixels):
        weighted_color_datum = np.copy(color_datum)
        weighted_color_datum[transparent_pixels] = 0

        sum_of_adjacent_opaque_pixels = np.zeros(color_datum.shape, int)
        sum_of_adjacent_opaque_pixels[:-1, :-1] += weighted_color_datum[1:, 1:]
        sum_of_adjacent_opaque_pixels[:, :-1] += weighted_color_datum[:, 1:]
        sum_of_adjacent_opaque_pixels[1:, :-1] += weighted_color_datum[:-1, 1:]
        sum_of_adjacent_opaque_pixels[:-1, :] += weighted_color_datum[1:, :]
        sum_of_adjacent_opaque_pixels[1:, :] += weighted_color_datum[:-1, :]
        sum_of_adjacent_opaque_pixels[:-1, 1:] += weighted_color_datum[1:, :-1]
        sum_of_adjacent_opaque_pixels[:, 1:] += weighted_color_datum[:, :-1]
        sum_of_adjacent_opaque_pixels[1:, 1:] += weighted_color_datum[:-1, :-1]

        return sum_of_adjacent_opaque_pixels
