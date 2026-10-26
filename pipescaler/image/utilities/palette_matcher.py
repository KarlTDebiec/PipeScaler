#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches the palette of one image to another."""

from __future__ import annotations

from typing import no_type_check

import numpy as np
from numba import njit
from PIL import Image

from pipescaler.core import Utility
from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.functions import get_palette
from pipescaler.image.core.numba import get_perceptually_weighted_distance

__all__ = ["PaletteMatcher"]


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

        best_fit_palette = np.zeros_like(fit_palette)
        for i, color in enumerate(fit_palette):
            # If color is available in reference palette, use it
            if tuple(color) in ref_palette_set:
                best_fit_palette[i] = color
                continue

            # If color is not available in reference palette, find the closest match
            _, best_fit_palette[i] = cls.get_best_fit_color_in_palette(
                color, ref_palette
            )

        return best_fit_palette

    @classmethod
    def run(  # ty: ignore[invalid-method-override]
        cls, ref_img: Image.Image, fit_img: Image.Image
    ) -> Image.Image:
        """Match the palette of an image to a reference.

        Arguments:
            ref_img: Image whose palette to use as reference
            fit_img: Image whose palette to fit to reference
        Returns:
            Image with palette fit to reference
        Raises:
            UnsupportedImageModeError: if an image mode is unsupported
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
