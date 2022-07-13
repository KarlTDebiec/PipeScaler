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
        mask_array = ~np.array(mask)

        while mask_array.sum() > 0:
            image_array, mask_array = self.run_iteration(image_array, mask_array)

        filled_image = Image.fromarray(image_array)
        if self.mask_fill_mode == MaskFillMode.MATCH_PALETTE:
            filled_image = self.palette_matcher.match_palette(image, filled_image)
        return filled_image

    def run_iteration(
        self, image_array: np.ndarray, mask_array: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Run one iteration of mask filling.

        Arguments:
            image_array: Image array
            mask_array: mask array
        Returns:
            image array with one additional round of pixel filling
        """
        # Count the number of opaque pixels adjacent to each pixel in image
        adjacent_opaque_pixels = self.adjacent_opaque_pixels(mask_array)

        # Disregard the number of adjacent opaque pixels for pixels that are themselves
        # opaque
        adjacent_opaque_pixels[np.logical_not(mask_array)] = 0

        # Identify pixels who have the max number of adjacent opaque pixels
        pixels_to_fill = np.logical_and(
            mask_array,
            adjacent_opaque_pixels == adjacent_opaque_pixels.max(),
        )

        # Calculate the color of pixels to fill
        sum_of_adjacent_opaque_pixels = self.sum_of_adjacent_opaque_pixels(
            image_array, mask_array
        )
        colors_of_pixels_to_fill = np.round(
            sum_of_adjacent_opaque_pixels[pixels_to_fill] / adjacent_opaque_pixels.max()
        ).astype(np.uint8)

        # Set colors, prepare updated mask, and return
        image_array[pixels_to_fill] = colors_of_pixels_to_fill
        mask_array = mask_array & ~pixels_to_fill
        return image_array, mask_array

    @staticmethod
    def adjacent_opaque_pixels(transparent_pixels: np.ndarray) -> np.ndarray:
        """Calculate the number of opaque pixels adjacent to each pixel.

        Arguments:
            transparent_pixels: Whether pixels are opaque
        Returns:
            Number of opaque pixels adjacent to each pixel
        """
        # Count total adjacent pixels
        adjacent_opaque_pixels = np.zeros(transparent_pixels.shape, int)
        adjacent_opaque_pixels[:-1, :-1] += 1
        adjacent_opaque_pixels[:, :-1] += 1
        adjacent_opaque_pixels[1:, :-1] += 1
        adjacent_opaque_pixels[:-1, :] += 1
        adjacent_opaque_pixels[1:, :] += 1
        adjacent_opaque_pixels[:-1, 1:] += 1
        adjacent_opaque_pixels[:, 1:] += 1
        adjacent_opaque_pixels[1:, 1:] += 1

        # Subtract transparent adjacent pixels
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
    def sum_of_adjacent_opaque_pixels(
        image_array: np.ndarray, transparent_pixels: np.ndarray
    ) -> np.ndarray:
        """Calculate the sum of color of opaque pixels adjacent to each pixel.

        Arguments:
            image_array: Image array
            transparent_pixels: Whether pixels are opaque
        Returns:
            Sum of color of opaque pixels adjacent to each pixel
        """
        weighted_color_array = np.copy(image_array)
        weighted_color_array[transparent_pixels] = 0

        sum_of_adjacent_opaque_pixels = np.zeros(image_array.shape, int)
        sum_of_adjacent_opaque_pixels[:-1, :-1] += weighted_color_array[1:, 1:]
        sum_of_adjacent_opaque_pixels[:, :-1] += weighted_color_array[:, 1:]
        sum_of_adjacent_opaque_pixels[1:, :-1] += weighted_color_array[:-1, 1:]
        sum_of_adjacent_opaque_pixels[:-1, :] += weighted_color_array[1:, :]
        sum_of_adjacent_opaque_pixels[1:, :] += weighted_color_array[:-1, :]
        sum_of_adjacent_opaque_pixels[:-1, 1:] += weighted_color_array[1:, :-1]
        sum_of_adjacent_opaque_pixels[:, 1:] += weighted_color_array[:, :-1]
        sum_of_adjacent_opaque_pixels[1:, 1:] += weighted_color_array[:-1, :-1]

        return sum_of_adjacent_opaque_pixels
