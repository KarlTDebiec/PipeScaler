#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Matches the palette of one image to another."""
import time
from typing import Union, no_type_check

import numba as nb
import numpy as np
from PIL import Image
from scipy.spatial.distance import cdist

from pipescaler.common import validate_enum, validate_int
from pipescaler.core import PaletteMatchMode, UnsupportedImageModeError, get_palette


class PaletteMatcher:
    """Matches the palette of one image to another."""

    def __init__(
        self,
        palette_match_mode: Union[type(PaletteMatchMode), str] = PaletteMatchMode.BASIC,
    ) -> None:
        """Validate and store static configuration."""
        self.palette_match_mode = validate_enum(palette_match_mode, PaletteMatchMode)

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

        # Match palette of fit image to that of reference image
        if self.palette_match_mode == PaletteMatchMode.BASIC:
            print()
            start = time.time()
            ref_palette = get_palette(ref_image).astype(np.uint8)
            print(f"ref_palette: {time.time() - start}")

            start = time.time()
            fit_palette = get_palette(fit_image).astype(np.uint8)
            print(f"fit_palette: {time.time() - start}")

            start = time.time()
            # noinspection PyTypeChecker
            fit_array = np.array(fit_image)
            fit_array_by_index = get_array_by_index(fit_array, fit_palette)
            print(f"fit_array_by_index: {time.time() - start}")

            start = time.time()
            best_fit_palette = get_best_fit_palette(fit_palette, ref_palette)
            print(f"best_fit_palette: {time.time() - start}")

            start = time.time()
            matched_array = get_array_by_color(fit_array_by_index, best_fit_palette)
            print(f"matched_array: {time.time() - start}")
        else:
            ref_palette = get_palette(ref_image).astype(np.uint8)
            # noinspection PyTypeChecker
            ref_array = np.array(ref_image)
            ref_array_by_index = get_array_by_index(ref_array, ref_palette)

            fit_palette = get_palette(fit_image).astype(np.uint8)
            # noinspection PyTypeChecker
            fit_array = np.array(fit_image)
            fit_array_by_index = get_array_by_index(fit_array, fit_palette)

            dist = self.get_weighted_distances(ref_palette, fit_palette)
            matched_array = self.get_local_match(
                fit_array_by_index, ref_array_by_index, ref_palette, dist
            )
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
            dist = cdist(ref_palette, fit_palette, get_weighted_distance)

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


def get_array_by_color(array_by_index: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Convert an array with indexed color and its palette to an array with full color.

    Args:
        array_by_index: Array whose values are the indexes of colors within palette
        palette: Palette to apply
    Returns:
        Array with full color
    """
    array = np.zeros((array_by_index.shape[0], array_by_index.shape[1], 3), np.uint8)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            array[i, j, :] = palette[array_by_index[i, j]]
    return array


def get_array_by_index(array: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Get palette-indexed version of image array.

    Args:
        array: Image array
        palette: Image palette
    Returns:
        Palette-indexed version of array
    """
    color_to_index = {tuple(color): i for i, color in enumerate(palette)}
    array_by_index = np.zeros((array.shape[0], array.shape[1]), np.int32)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            array_by_index[i, j] = color_to_index[tuple(array[i, j])]

    return array_by_index


def get_best_fit_palette(fit_palette, ref_palette):
    """Get a palette drawn from ref_palette that is most similar to fit_palette.

    Args:
        fit_palette: Palette to fit
        ref_palette: Reference palette
    Returns:
        Palette whose size matches that of fit_palette, and whose colors are those from
        ref_palette that are most similar to fit_palette
    """
    ref_palette_set = set([tuple(color) for color in ref_palette])
    ref_palette_by_cell = get_palette_by_cell(ref_palette)

    best_fit_palette = np.zeros(fit_palette.shape, np.uint8)
    for i, color in enumerate(fit_palette):
        # If color is available in ref_palette, use it
        if tuple(color) in ref_palette_set:
            best_fit_palette[i] = color
            continue

        # If color is not available in ref_palette, find the closest match
        best_dist = None
        best_color = None
        cell = (color[0] // 16, color[1] // 16, color[2] // 16)
        for red_i in range(max(0, cell[0] - 1), min(15, cell[0] + 1) + 1):
            for green_i in range(max(0, cell[1] - 1), min(15, cell[1] + 1) + 1):
                for blue_i in range(max(0, cell[2] - 1), min(15, cell[2] + 1) + 1):
                    if (red_i, green_i, blue_i) not in ref_palette_by_cell:
                        continue
                    candidate_colors = ref_palette_by_cell[(red_i, green_i, blue_i)]
                    best_dist_in_cell, best_color_in_cell = get_closest_color(
                        color, candidate_colors
                    )
                    if best_dist is None or best_dist_in_cell < best_dist:
                        best_dist = best_dist_in_cell
                        best_color = best_color_in_cell
        best_fit_palette[i] = best_color

    return best_fit_palette


def get_palette_by_cell(palette: np.ndarray) -> dict[tuple[int, int, int], np.ndarray]:
    """Reorganize palette into 16x16x16 cells within the 256x256x256 rgb space.

    For example, the key (1, 2, 3) would contain an array of colors whose red channel
    is between 16 and 31, whose blue channel is between 32 and 47, and whose green
    channel is between 48 and 63. The red, blue, and green dimensions each range between
    0 and 15, yielding up to 4,096 keys. Keys whose corresponding cell does not have
    any colors in the palette are excluded.

    Output dict streamlines searching a palette for colors close to a source color.

    Args:
        palette: Complete palette
    Returns:
        dict whose keys are a tuple of cell coordinates in the red, green and blue
        dimensions, and whose values are an array of palette colors each chell
    """
    palette_by_cell = {}

    for color in palette:
        cell = (color[0] // 16, color[1] // 16, color[2] // 16)
        if cell not in palette_by_cell:
            palette_by_cell[cell] = []
        palette_by_cell[cell].append(color)

    for cell in palette_by_cell:
        palette_by_cell[cell] = np.array(palette_by_cell[cell])

    return palette_by_cell


@no_type_check
@nb.njit(nogil=True, cache=True, fastmath=True)
def get_closest_color(
    color: np.ndarray, palette: np.ndarray
) -> tuple[float, np.ndarray]:
    """Get the color in a palette most similar to a provided color.

    Args:
        color: Color to match
        palette: Palette to which to match
    Returns:
        Weighted distance between color and its closest match, and closest match
    """
    best_dist = -1.0
    best_color = np.array([0, 0, 0], np.uint8)
    for candidate_color in palette:
        dist = get_weighted_distance(color, candidate_color)
        if best_dist < 0 or dist < best_dist:
            best_dist = dist
            best_color = candidate_color

    return best_dist, best_color


@no_type_check
@nb.njit(nogil=True, cache=True, fastmath=True)
def get_weighted_distance(color_1: np.ndarray, color_2: np.ndarray) -> float:
    """Get the squared distance between two colors, adjusted for perception.

    Arguments:
        color_1: Color 1
        color_2: Color 2
    Returns:
        Squared distance between two colors
    """
    rmean = (color_1[0] + color_2[0]) / 2
    dr = color_1[0] - color_2[0]
    dg = color_1[1] - color_2[1]
    db = color_1[2] - color_2[2]
    return (
        ((2 + (rmean / 256)) * (dr**2))
        + (4 * (dg**2))
        + ((2 + ((255 - rmean) / 256)) * (db**2))
    )
