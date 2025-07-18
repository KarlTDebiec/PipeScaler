#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches the palette of one image to another."""

from __future__ import annotations

from itertools import product
from typing import no_type_check

import numpy as np
from numba import njit
from PIL import Image

from pipescaler.core import Utility
from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.functions import get_palette
from pipescaler.image.core.numba import get_perceptually_weighted_distance


class PaletteMatcher(Utility):
    """Matches the palette of one image to another."""

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
        ref_palette_set = {tuple(color) for color in ref_palette}
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
    ) -> np.ndarray | None:
        """Get best fit color drawn from a palette, searching within nearby cells.

        Arguments:
            color: Color to find best match of
            ref_palette_by_cell: Palette to draw from, divided into cells
        Returns:
            Color in palette most similar to provided color
        """
        # Prepare set of cells to check
        cell = tuple(int(c) // 16 for c in color)
        cell_range = 0
        cells_to_check: set[tuple[int, int, int]] = set()
        while len(cells_to_check) == 0:
            cell_range += 1
            cell_ranges = [
                range(max(0, cell[i] - cell_range), min(15, cell[i] + cell_range) + 1)
                for i in range(3)
            ]
            cells_to_check = set(product(*cell_ranges))  # type: ignore
            cells_to_check = cells_to_check.intersection(ref_palette_by_cell)

        # Search cells for best match color
        best_dist = None
        best_color = None
        for cell_to_check in cells_to_check:
            best_dist_in_cell, best_color_in_cell = cls.get_best_fit_color_in_palette(
                color, ref_palette_by_cell[cell_to_check]
            )
            if best_dist is None or best_dist_in_cell < best_dist:
                best_dist = best_dist_in_cell
                best_color = best_color_in_cell

        return best_color

    @classmethod
    def run(cls, ref_img: Image.Image, fit_img: Image.Image) -> Image.Image:
        """Match the palette of an image to a reference.

        Arguments:
            ref_img: Image whose palette to use as reference
            fit_img: Image whose palette to fit to reference
        Returns:
            Image with palette fit to reference
        """
        if ref_img.mode != fit_img.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_img.mode}' of reference image does not match mode "
                f"'{fit_img.mode}' of fit image"
            )
        ref_palette = get_palette(ref_img).astype(np.uint8)
        fit_palette = get_palette(fit_img).astype(np.uint8)
        fit_arr = np.array(fit_img)

        if fit_img.mode == "L":
            color_to_index = {color: i for i, color in enumerate(fit_palette)}
            fit_arr_by_index = np.zeros(fit_arr.shape[:2], np.int32)
            for i in range(fit_arr.shape[0]):
                for j in range(fit_arr.shape[1]):
                    fit_arr_by_index[i, j] = color_to_index[fit_arr[i, j]]
            dist = (ref_palette.astype(float) - fit_palette.astype(float)[:, None]) ** 2
            best_fit_palette = ref_palette[dist.argmin(axis=1)]
            matched_arr = np.zeros_like(fit_arr)
            for i in range(fit_arr.shape[0]):
                for j in range(fit_arr.shape[1]):
                    matched_arr[i, j] = best_fit_palette[fit_arr_by_index[i, j]]
        else:
            fit_arr_by_index = cls.get_indexed_array_from_rgb_array(
                fit_arr, fit_palette
            )
            best_fit_palette = cls.get_best_fit_palette(fit_palette, ref_palette)
            matched_arr = cls.get_rgb_array_from_indexed_array(
                fit_arr_by_index, best_fit_palette
            )

        matched_img = Image.fromarray(matched_arr)
        return matched_img

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
        rgb_arr: np.ndarray, palette: np.ndarray
    ) -> np.ndarray:
        """Convert RGB image array to indexed image array using provided palette.

        Arguments:
            rgb_arr: Array whose values are the RGB channels of an image
            palette: Image palette
        Returns:
            Array whose values are the indexes of colors within palette
        """
        color_to_index = {tuple(color): i for i, color in enumerate(palette)}
        indexed_arr = np.zeros(rgb_arr.shape[:2], np.int32)
        for i in range(rgb_arr.shape[0]):
            for j in range(rgb_arr.shape[1]):
                indexed_arr[i, j] = color_to_index[tuple(rgb_arr[i, j])]

        return indexed_arr

    @staticmethod
    def get_palette_by_cell(
        palette: np.ndarray,
    ) -> dict[tuple[int, int, int], np.ndarray]:
        """Reorganize palette into 16x16x16 cells within the 256x256x256 rgb space.

        For example, the key (1, 2, 3) would contain an rgb_arr of colors whose red
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
            and blue dimensions, and whose values are an rgb_arr of palette colors
            each cell contains
        """
        palette_by_cell_list: dict[tuple[int, int, int], list[int]] = {}

        for color in palette:
            cell = (color[0] // 16, color[1] // 16, color[2] // 16)
            if cell not in palette_by_cell_list:
                palette_by_cell_list[cell] = []
            palette_by_cell_list[cell].append(color)

        palette_by_cell_arr: dict[tuple[int, int, int], np.ndarray] = {}
        for cell, cell_palette in palette_by_cell_list.items():
            palette_by_cell_arr[cell] = np.array(cell_palette)

        return palette_by_cell_arr

    @staticmethod
    def get_rgb_array_from_indexed_array(
        indexed_arr: np.ndarray, palette: np.ndarray
    ) -> np.ndarray:
        """Convert indexed image array to RGB image using provided palette.

        Arguments:
            indexed_arr: Array whose values are the indexes of colors within palette
            palette: Image palette
        Returns:
            Array whose values are the RGB channels of an image
        """
        rgb_arr = np.zeros((*indexed_arr.shape[:2], 3), np.uint8)
        for i in range(indexed_arr.shape[0]):
            for j in range(indexed_arr.shape[1]):
                rgb_arr[i, j, :] = palette[indexed_arr[i, j]]

        return rgb_arr
