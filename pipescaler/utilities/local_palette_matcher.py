#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Matches the palette of one image to another."""
import time
from typing import no_type_check

import numba as nb
import numpy as np
from PIL import Image
from scipy.spatial.distance import cdist

from pipescaler.common import validate_int
from pipescaler.core import UnsupportedImageModeError, get_palette
from pipescaler.core.image import get_perceptually_weighted_distance


class LocalPaletteMatcher:
    """Matches the palette of one image to another."""

    def match_palette(
        self, ref_image: Image.Image, fit_image: Image.Image
    ) -> Image.Image:
        """Match the palette of an image to a reference.

        Arguments:
            ref_image: Image whose palette to use as reference
            fit_image: Image whose palette to fit to reference
        Returns:
            Image with palette fit to reference
        """
        if ref_image.mode != fit_image.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_image.mode}' of reference image does not match mode "
                f"'{fit_image.mode}' of fit image"
            )

        print()

        start = time.time()
        ref_palette = get_palette(ref_image).astype(np.uint8)
        print(f"ref_palette ({ref_palette.shape}): {time.time() - start}")

        start = time.time()
        # noinspection PyTypeChecker
        ref_array = np.array(ref_image)
        ref_array_by_index = get_array_by_index(ref_array, ref_palette)
        print(f"ref_array_by_index: {time.time() - start}")

        start = time.time()
        fit_palette = get_palette(fit_image).astype(np.uint8)
        print(f"fit_palette ({fit_palette.shape}): {time.time() - start}")

        start = time.time()
        # noinspection PyTypeChecker
        fit_array = np.array(fit_image)
        fit_array_by_index = get_array_by_index(fit_array, fit_palette)
        print(f"fit_array_by_index: {time.time() - start}")

        start = time.time()
        dist = self.get_weighted_distances(ref_palette, fit_palette)
        print(f"dist ({dist.shape}): {time.time() - start}")

        start = time.time()
        matched_array = self.get_local_match(
            fit_array_by_index, ref_array_by_index, ref_palette, dist
        )
        print(f"matched_array ({matched_array.shape}): {time.time() - start}")

        matched_image = Image.fromarray(matched_array)
        return matched_image

    @classmethod
    def get_local_match(cls, fit_array_by_index, ref_array_by_index, ref_palette, dist):
        # Replace each fit pixel's color with the closest reference color observed
        # in a 3x3 window around the fit pixel's corresponding reference pixel
        scale = validate_int(fit_array_by_index.shape[0] / ref_array_by_index.shape[0])
        local_colors = cls.get_local_colors(ref_array_by_index)

        output_array_by_index = cls.get_best_local_color(
            fit_array_by_index, local_colors, scale, dist
        )

        if len(ref_palette.shape) == 1:
            matched_array = np.zeros(fit_array_by_index.shape, np.uint8)
        else:
            matched_array = np.zeros((*fit_array_by_index.shape, 3), np.uint8)
        for i, color in enumerate(ref_palette):
            matched_array[output_array_by_index == i] = color

        return matched_array

    @no_type_check
    @staticmethod
    @nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
    def get_best_local_color(fit_array_by_index, local_colors, scale, dist):
        output_array_by_index = np.zeros_like(fit_array_by_index)
        for fit_x in range(fit_array_by_index.shape[0]):
            for fit_y in range(fit_array_by_index.shape[1]):
                ref_x = int(np.floor(fit_x / scale))
                ref_y = int(np.floor(fit_y / scale))

                best_i = -1
                for i in range(dist[:, fit_array_by_index[fit_x, fit_y]].size):
                    if local_colors[ref_x, ref_y, i] and (
                        best_i == -1
                        or dist[i, fit_array_by_index[fit_x, fit_y]]
                        < dist[best_i, fit_array_by_index[fit_x, fit_y]]
                    ):
                        best_i = i

                output_array_by_index[fit_x, fit_y] = best_i
        return output_array_by_index

    @classmethod
    def get_weighted_distances(cls, ref_palette, fit_palette):
        if len(ref_palette.shape) == 1:
            # Calculate distance between all reference and fit colors
            dist = np.zeros((ref_palette.size, fit_palette.size), float)
            for i, ref_color in enumerate(ref_palette):
                for j, fit_color in enumerate(fit_palette):
                    dist[i, j] = (ref_color - fit_color) ** 2
        else:
            dist = cdist(ref_palette, fit_palette, get_perceptually_weighted_distance)

        return dist

    @staticmethod
    def get_local_colors(array_by_index):
        local_colors = np.zeros((*array_by_index.shape, array_by_index.max() + 1), bool)
        for i in range(array_by_index.max() + 1):
            equal_i = array_by_index == i
            local_colors[equal_i, i] = True
            local_colors[:-1, :-1, i] = local_colors[:-1, :-1, i] | equal_i[1:, 1:]
            local_colors[:, :-1, i] = local_colors[:, :-1, i] | equal_i[:, 1:]
            local_colors[1:, :-1, i] = local_colors[1:, :-1, i] | equal_i[:-1, 1:]
            local_colors[:-1, :, i] = local_colors[:-1, :, i] | equal_i[1:, :]
            local_colors[1:, :, i] = local_colors[1:, :, i] | equal_i[:-1, :]
            local_colors[:-1, 1:, i] = local_colors[:-1, 1:, i] | equal_i[1:, :-1]
            local_colors[:, 1:, i] = local_colors[:, 1:, i] | equal_i[:, :-1]
            local_colors[1:, 1:, i] = local_colors[1:, 1:, i] | equal_i[:-1, :-1]

        return local_colors


def get_array_by_index(array: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Get palette-indexed version of image rgb_array.

    Arguments:
        array: Image rgb_array
        palette: Image palette
    Returns:
        Palette-indexed version of rgb_array
    """
    color_to_index = {tuple(color): i for i, color in enumerate(palette)}
    array_by_index = np.zeros((array.shape[0], array.shape[1]), np.int32)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            array_by_index[i, j] = color_to_index[tuple(array[i, j])]

    return array_by_index
