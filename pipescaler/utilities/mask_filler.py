#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Erases masked pixels within an image."""
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
        adjacent_opaque_pixels = dict()
        pixels_to_recount = pixels_to_fill.copy()
        while len(pixels_to_fill) > 0:
            print(
                f"iteration {iteration}, pixels_to_fill={len(pixels_to_fill)}, "
                f"pixels_to_recount={len(pixels_to_recount)}"
            )
            (
                image_array,
                pixels_to_fill,
                adjacent_opaque_pixels,
                pixels_to_recount,
            ) = self.run_iteration(
                image_array, pixels_to_fill, adjacent_opaque_pixels, pixels_to_recount
            )
            # Image.fromarray(image_array).show()
            iteration += 1

        # Return image
        filled_image = Image.fromarray(image_array)
        if self.mask_fill_mode == MaskFillMode.MATCH_PALETTE:
            filled_image = self.palette_matcher.match_palette(image, filled_image)
        return filled_image

    def run_iteration(
        self,
        image_array: np.ndarray,
        pixels_to_fill: set[tuple[int, int]],
        adjacent_opaque_pixels: dict[tuple[int, int], int],
        pixels_to_recount: set[tuple[int, int]],
    ) -> tuple[
        np.ndarray,
        set[tuple[int, int]],
        dict[tuple[int, int], int],
        set[tuple[int, int]],
    ]:
        width = image_array.shape[0]
        height = image_array.shape[1]

        # Count number of opaque pixels adjacent to each pixel to be filled
        for pixel in pixels_to_recount:
            count = 0
            for x_p in range(max(0, pixel[0] - 1), min(width, pixel[0] + 2)):
                for y_p in range(max(0, pixel[1] - 1), min(height, pixel[1] + 2)):
                    if (x_p, y_p) not in pixels_to_fill:
                        count += 1
            adjacent_opaque_pixels[pixel] = count

        count = max(adjacent_opaque_pixels.values())
        pixels_to_fill_next_iter = set()
        pixels_to_recount_next_iter = set()
        for pixel in pixels_to_fill:
            if adjacent_opaque_pixels[pixel] == count:
                color = np.zeros(3, dtype=np.uint32)
                for x_p in range(max(0, pixel[0] - 1), min(width, pixel[0] + 2)):
                    for y_p in range(max(0, pixel[1] - 1), min(height, pixel[1] + 2)):
                        if (x_p, y_p) == pixel:
                            continue
                        if (x_p, y_p) not in pixels_to_fill:
                            color += image_array[x_p, y_p]
                        elif (
                            x_p,
                            y_p,
                        ) in adjacent_opaque_pixels and adjacent_opaque_pixels[
                            (x_p, y_p)
                        ] != count:
                            pixels_to_recount_next_iter.add((x_p, y_p))
                image_array[pixel[0], pixel[1]] = color // count
                adjacent_opaque_pixels.pop(pixel)
            else:
                pixels_to_fill_next_iter.add(pixel)

        return (
            image_array,
            pixels_to_fill_next_iter,
            adjacent_opaque_pixels,
            pixels_to_recount_next_iter,
        )
