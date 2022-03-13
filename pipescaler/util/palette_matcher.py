#!/usr/bin/env python
#   pipescaler/util/mask_filler.py
#
#   Copyright (C) 2017-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
Matches the palette of one image to another.
"""
from typing import Union

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
        if ref_image.mode != fit_image.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_image.mode}' of reference image does not match mode "
                f"'{fit_image.mode}' of fit image"
            )

        # Get colors in reference and fit images
        ref_palette, ref_array_by_index = self.get_palette_and_array_by_index(ref_image)
        fit_palette, fit_array_by_index = self.get_palette_and_array_by_index(fit_image)

        # Calculate weighted distance between all reference and fit colors
        dist = self.get_weighted_distances(ref_palette, fit_palette)

        # Match palette of fit image to that of reference image
        if self.palette_match_mode == PaletteMatchMode.BASIC:
            matched_array = self.get_basic_match(fit_array_by_index, ref_palette, dist)
        else:
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

        output_array_by_index = np.zeros_like(fit_array_by_index)
        for fit_x in range(fit_array_by_index.shape[0]):
            for fit_y in range(fit_array_by_index.shape[1]):
                ref_x = int(np.floor(fit_x / scale))
                ref_y = int(np.floor(fit_y / scale))

                dist_xy = np.copy(dist[:, fit_array_by_index[fit_x, fit_y]])
                dist_xy[~local_colors[ref_x, ref_y]] = np.nan
                best = np.nanargmin(dist_xy)
                output_array_by_index[fit_x, fit_y] = best

        if len(ref_palette.shape) == 1:
            matched_array = np.zeros(fit_array_by_index.shape, np.uint8)
        else:
            matched_array = np.zeros((*fit_array_by_index.shape, 3), np.uint8)
        for i, color in enumerate(ref_palette):
            matched_array[output_array_by_index == i] = color
        return matched_array

    @classmethod
    def get_weighted_distances(cls, ref_palette, fit_palette):
        if len(ref_palette.shape) == 1:
            # Calculate distance between all reference and fit colors
            dist = np.zeros((ref_palette.size, fit_palette.size), float)
            for i, ref_color in enumerate(ref_palette):
                for j, fit_color in enumerate(fit_palette):
                    dist[i, j] = (ref_color - fit_color) ** 2
        else:
            dist = cdist(ref_palette, fit_palette, cls.get_weighted_distance)

        return dist

    @staticmethod
    def get_basic_match(fit_array_by_index, ref_palette, dist):
        """Replace each fit pixel's color with the closest reference color."""
        if len(ref_palette.shape) == 1:
            matched_array = np.zeros(fit_array_by_index.shape, np.uint8)
        else:
            matched_array = np.zeros((*fit_array_by_index.shape, 3), np.uint8)
        for fit_index, ref_index in enumerate(dist.argmin(axis=0)):
            matched_array[fit_array_by_index == fit_index] = ref_palette[ref_index]
        return matched_array

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

    @staticmethod
    def get_palette_and_array_by_index(image: Image.Image):
        # noinspection PyTypeChecker
        array = np.array(image)
        palette = get_palette(image)

        if image.mode == "L":
            array_by_index = np.zeros(array.shape, int)
            for i, color in enumerate(palette):
                array_by_index[array == color] = i
        else:
            array_by_index = np.zeros(array.shape[:-1], int)
            for i, color in enumerate(palette):
                array_by_index[np.all(array == color, axis=2)] = i

        return palette, array_by_index

    @staticmethod
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
