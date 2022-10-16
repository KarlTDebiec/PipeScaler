#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Erases masked pixels within an image."""
from itertools import chain
from typing import Union

import numpy as np
from PIL import Image

from pipescaler.common import validate_enum
from pipescaler.core import Utility
from pipescaler.core.enums import MaskFillMode
from pipescaler.utilities.palette_matcher import PaletteMatcher


class MaskFiller(Utility):
    """Erases masked pixels within an image."""

    def __init__(
        self, mask_fill_mode: Union[MaskFillMode, str] = MaskFillMode.BASIC
    ) -> None:
        """Validate and store static configuration and initialize.

        Arguments:
            mask_fill_mode: Mode to use for mask filling
        """
        self.mask_fill_mode = validate_enum(mask_fill_mode, MaskFillMode)
        if self.mask_fill_mode == MaskFillMode.MATCH_PALETTE:
            self.palette_matcher = PaletteMatcher()

    def fill(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """Erases masked pixels within an image.

        Each erased pixel is replaced with the average color of adjacent unmasked
        pixels, iteratively.

        Arguments:
            image: Image
            mask: Mask
        Returns:
            Image with masked pixels replaced
        """
        image_array = np.array(image)
        mask_array = np.array(mask)

        # Get all pixels to be filled
        pixels_to_fill = set()
        for x in range(mask_array.shape[0]):
            for y in range(mask_array.shape[1]):
                if mask_array[x, y]:
                    pixels_to_fill.add((x, y))

        # Iterate until no pixels remain to be filled
        iteration = 0
        while len(pixels_to_fill) > 0:
            print(f"iteration {iteration}, {len(pixels_to_fill)} pixels to fill")
            image_array, pixels_to_fill = self.run_iteration(
                image_array, pixels_to_fill
            )
            iteration += 1

        # Return image
        filled_image = Image.fromarray(image_array)
        if self.mask_fill_mode == MaskFillMode.MATCH_PALETTE:
            filled_image = self.palette_matcher.match_palette(image, filled_image)
        return filled_image

    def run_iteration(
        self, image_array: np.ndarray, pixels_to_fill: set[tuple[int, int]]
    ) -> tuple[np.ndarray, set[tuple[int, int]]]:
        width = image_array.shape[0]
        height = image_array.shape[1]

        # Count number of opaque pixels adjacent to each pixel to be filled
        adjacent_opaque_pixels = dict()
        for pixel_to_fill in pixels_to_fill:
            x, y = pixel_to_fill
            count = 0
            for x_p in range(max(0, x - 1), min(width, x + 2)):
                for y_p in range(max(0, y - 1), min(height, y + 2)):
                    if (x_p, y_p) not in pixels_to_fill:
                        count += 1
            if count not in adjacent_opaque_pixels:
                adjacent_opaque_pixels[count] = set()
            adjacent_opaque_pixels[count].add(pixel_to_fill)

        count = max(adjacent_opaque_pixels)
        for pixel_to_fill in adjacent_opaque_pixels.pop(count):
            x, y = pixel_to_fill
            pixel_sum = np.zeros(3, dtype=np.uint32)
            for x_p in range(max(0, x - 1), min(width, x + 2)):
                for y_p in range(max(0, y - 1), min(height, y + 2)):
                    if (x_p, y_p) not in pixels_to_fill:
                        pixel_sum += image_array[x_p, y_p]
            pixel_sum //= count
            image_array[x, y] = pixel_sum

        remaining_pixels_to_fill = set(
            chain.from_iterable(adjacent_opaque_pixels.values())
        )

        return image_array, remaining_pixels_to_fill
