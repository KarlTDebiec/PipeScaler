#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Matches the palette of one image to another."""
from itertools import product
from typing import Optional, no_type_check

import numpy as np
from numba import njit
from PIL import Image

from pipescaler.core import UnsupportedImageModeError, get_palette
from pipescaler.core.image import get_perceptually_weighted_distance


class PaletteMatcher:
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
        ref_palette = get_palette(ref_image).astype(np.uint8)
        fit_palette = get_palette(fit_image).astype(np.uint8)
        # noinspection PyTypeChecker
        fit_array = np.array(fit_image)
        if fit_image.mode == "L":
            color_to_index = {color: i for i, color in enumerate(fit_palette)}
            fit_array_by_index = np.zeros(fit_array.shape[:2], np.int32)
            for i in range(fit_array.shape[0]):
                for j in range(fit_array.shape[1]):
                    fit_array_by_index[i, j] = color_to_index[fit_array[i, j]]
            dist = (ref_palette.astype(float) - fit_palette.astype(float)[:, None]) ** 2
            best_fit_palette = ref_palette[dist.argmin(axis=1)]
            matched_array = np.zeros_like(fit_array)
            for i in range(fit_array.shape[0]):
                for j in range(fit_array.shape[1]):
                    matched_array[i, j] = best_fit_palette[fit_array_by_index[i, j]]
        else:
            fit_array_by_index = self.get_indexed_array_from_rgb_array(
                fit_array, fit_palette
            )
            best_fit_palette = self.get_best_fit_palette(fit_palette, ref_palette)
            matched_array = self.get_rgb_array_from_indexed_array(
                fit_array_by_index, best_fit_palette
            )

        matched_image = Image.fromarray(matched_array)
        return matched_image

    @classmethod
    def get_best_fit_palette(
        cls, fit_palette: np.ndarray, ref_palette: np.ndarray
    ) -> np.ndarray:
        """Get palette drawn from ref_palette that is most similar to fit_palette.

        Arguments:
            fit_palette: Palette to fit
            ref_palette: Reference palette
        Returns:
            Palette whose size matches that of fit_palette, and whose colors are those
            from ref_palette that are most similar to fit_palette
        """
        ref_palette_set = set([tuple(color) for color in ref_palette])
        ref_palette_by_cell = cls.get_palette_by_cell(ref_palette)

        best_fit_palette = np.zeros_like(fit_palette)
        for i, color in enumerate(fit_palette):
            # If color is available in reference palette, use it
            if tuple(color) in ref_palette_set:
                best_fit_palette[i] = color
                continue

            # If color is not available in reference palette, find the closest match
            best_fit_palette[i] = cls.get_best_fit_color_by_cell(
                color, ref_palette_by_cell
            )

        return best_fit_palette

    @classmethod
    def get_best_fit_color_by_cell(
        cls,
        color: np.ndarray,
        ref_palette_by_cell: dict[tuple[int, int, int], np.ndarray],
    ) -> Optional[np.ndarray]:
        """Get best fit color drawn from a palette, searching within nearby cells.

        Arguments:
            color: Color to find best match of
            ref_palette_by_cell: Palette to draw from, divided into cells
        Returns:
            Color in palette most similar to provided color
        """
        # Prepare set of cells to check
        cell = (color[0] // 16, color[1] // 16, color[2] // 16)
        cell_range = 0
        cells_to_check = set()
        while len(cells_to_check) == 0:
            cell_range += 1
            cell_ranges = [
                range(max(0, cell[i] - cell_range), min(15, cell[i] + cell_range) + 1)
                for i in range(3)
            ]
            cells_to_check = set(product(*cell_ranges)).intersection(
                ref_palette_by_cell
            )

        # Search cells for best match color
        best_dist = None
        best_color = None
        for cell_to_check in cells_to_check:
            # noinspection PyTypeChecker
            best_dist_in_cell, best_color_in_cell = cls.get_best_fit_color_in_palette(
                color, ref_palette_by_cell[cell_to_check]
            )
            if best_dist is None or best_dist_in_cell < best_dist:
                best_dist = best_dist_in_cell
                best_color = best_color_in_cell

        return best_color

    @no_type_check
    @staticmethod
    @njit(nogil=True, cache=True, fastmath=True)
    def get_best_fit_color_in_palette(
        color: np.ndarray, palette: np.ndarray
    ) -> tuple[float, np.ndarray]:
        """Get the color in a palette most similar to a provided color.

        Arguments:
            color: Color to match
            palette: Palette to which to match
        Returns:
            Weighted distance between color and its closest match, and closest match
        """
        best_dist = -1.0
        best_color = np.array([0, 0, 0], np.uint8)
        for candidate_color in palette:
            dist = get_perceptually_weighted_distance(color, candidate_color)
            if best_dist < 0 or dist < best_dist:
                best_dist = dist
                best_color = candidate_color

        return best_dist, best_color

    @staticmethod
    def get_indexed_array_from_rgb_array(
        rgb_array: np.ndarray, palette: np.ndarray
    ) -> np.ndarray:
        """Convert RGB image array to indexed image array using provided palette.

        Arguments:
            rgb_array: Array whose values are the RGB channels of an image
            palette: Image palette
        Returns:
            Array whose values are the indexes of colors within palette
        """
        color_to_index = {tuple(color): i for i, color in enumerate(palette)}
        indexed_array = np.zeros(rgb_array.shape[:2], np.int32)
        for i in range(rgb_array.shape[0]):
            for j in range(rgb_array.shape[1]):
                indexed_array[i, j] = color_to_index[tuple(rgb_array[i, j])]

        return indexed_array

    @staticmethod
    def get_palette_by_cell(
        palette: np.ndarray,
    ) -> dict[tuple[int, int, int], np.ndarray]:
        """Reorganize palette into 16x16x16 cells within the 256x256x256 rgb space.

        For example, the key (1, 2, 3) would contain an rgb_array of colors whose red
        channel is between 16 and 31, whose blue channel is between 32 and 47, and whose
        green channel is between 48 and 63. The red, blue, and green dimensions each
        range between 0 and 15, yielding up to 4,096 keys. Keys whose corresponding
        cell_to_check does not have any colors in the palette are excluded from the
        dict.

        The resulting output dict narrows down the search for the color in a palette
        most similar to a specific provided color.

        Arguments:
            palette: Complete palette
        Returns:
            dict whose keys are a tuple of cell_to_check coordinates in the red, green
            and blue dimensions, and whose values are an rgb_array of palette colors
            each chell
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

    @staticmethod
    def get_rgb_array_from_indexed_array(
        indexed_array: np.ndarray, palette: np.ndarray
    ) -> np.ndarray:
        """Convert indexed image array to RGB image using provided palette.

        Arguments:
            indexed_array: Array whose values are the indexes of colors within palette
            palette: Image palette
        Returns:
            Array whose values are the RGB channels of an image
        """
        rgb_array = np.zeros((*indexed_array.shape[:2], 3), np.uint8)
        for i in range(indexed_array.shape[0]):
            for j in range(indexed_array.shape[1]):
                rgb_array[i, j, :] = palette[indexed_array[i, j]]

        return rgb_array
