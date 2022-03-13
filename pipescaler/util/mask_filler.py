#!/usr/bin/env python
#   pipescaler/util/mask_filler.py
#
#   Copyright (C) 2017-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
Erases masked pixels within an image.
"""
from typing import Tuple

import numpy as np
from PIL import Image


class MaskFiller:
    """Erases masked pixels within an image.

    Replaces the color of each masked pixel with the average color of adjacent unmasked
    pixels, iteratively.
    """

    def fill_mask(
        self, color_image: Image.Image, mask_image: Image.Image
    ) -> Image.Image:
        """
        Erases masked pixels within an image, replacing the color of each masked pixel with
        the average color of adjacent unmasked pixels, iteratively

        Arguments:
            color_image: Image
            mask_image: Mask
        Returns:
            Image with masked pixels replaced
        """

        # noinspection PyTypeChecker
        color_array = np.array(color_image)
        # noinspection PyTypeChecker
        mask_array = ~np.array(mask_image)

        while mask_array.sum() > 0:
            color_array, mask_array = self.run_iteration(color_array, mask_array)

        return Image.fromarray(color_array)

    def run_iteration(
        self, color_array: np.ndarray, mask_array: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:

        # count the number of opaque pixels adjacent to each pixel in image
        adjacent_opaque_pixels = self.adjacent_opaque_pixels(mask_array)

        # Disregard the number of adjacent opaque pixels for pixels that are themselves
        # opaque
        adjacent_opaque_pixels[np.logical_not(mask_array)] = 0

        # Identify pixels who have the max number of adjacent opaque pixels
        # noinspection PyArgumentList
        pixels_to_fill = np.logical_and(
            mask_array,
            adjacent_opaque_pixels == adjacent_opaque_pixels.max(),
        )

        # Calculate the color of pixels to fill
        sum_of_adjacent_opaque_pixels = self.sum_of_adjacent_opaque_pixels(
            color_array, mask_array
        )
        # noinspection PyArgumentList
        colors_of_pixels_to_fill = np.round(
            sum_of_adjacent_opaque_pixels[pixels_to_fill] / adjacent_opaque_pixels.max()
        ).astype(np.uint8)

        # Set colors, prepare updated mask, and return
        color_array[pixels_to_fill] = colors_of_pixels_to_fill
        mask_array = mask_array & ~pixels_to_fill
        return color_array, mask_array

    @staticmethod
    def adjacent_opaque_pixels(transparent_pixels):
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
    def sum_of_adjacent_opaque_pixels(color_array, transparent_pixels):
        weighted_color_array = np.copy(color_array)
        weighted_color_array[transparent_pixels] = 0

        sum_of_adjacent_opaque_pixels = np.zeros(color_array.shape, int)
        sum_of_adjacent_opaque_pixels[:-1, :-1] += weighted_color_array[1:, 1:]
        sum_of_adjacent_opaque_pixels[:, :-1] += weighted_color_array[:, 1:]
        sum_of_adjacent_opaque_pixels[1:, :-1] += weighted_color_array[:-1, 1:]
        sum_of_adjacent_opaque_pixels[:-1, :] += weighted_color_array[1:, :]
        sum_of_adjacent_opaque_pixels[1:, :] += weighted_color_array[:-1, :]
        sum_of_adjacent_opaque_pixels[:-1, 1:] += weighted_color_array[1:, :-1]
        sum_of_adjacent_opaque_pixels[:, 1:] += weighted_color_array[:, :-1]
        sum_of_adjacent_opaque_pixels[1:, 1:] += weighted_color_array[:-1, :-1]

        return sum_of_adjacent_opaque_pixels
