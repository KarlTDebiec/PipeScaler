#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches the palette of one image to another, restricted to nearby colors."""

from __future__ import annotations

from typing import no_type_check

import numpy as np
from numba import njit
from PIL import Image

from pipescaler.core import Utility
from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.core.numba import get_perceptually_weighted_distance


class LocalPaletteMatcher(Utility):
    """Matches the palette of one image to another, restricted to nearby colors."""

    @classmethod
    def run(
        cls, ref_img: Image.Image, fit_img: Image.Image, local_range: int = 1
    ) -> Image.Image:
        """Match the palette of an image to a reference.

        Arguments:
            ref_img: Image whose palette to use as reference
            fit_img: Image whose palette to fit to reference
            local_range: Range of adjacent pixels from which to draw best-fit color
        Returns:
            Image with palette fit to reference
        """
        if ref_img.mode != fit_img.mode:
            raise UnsupportedImageModeError(
                f"Image mode '{ref_img.mode}' of reference image does not match mode "
                f"'{fit_img.mode}' of fit image"
            )
        ref_arr = np.array(ref_img)
        fit_arr = np.array(fit_img)

        if fit_img.mode == "L":
            matched_arr = cls.get_local_match_l(fit_arr, ref_arr, local_range)
        else:
            matched_arr = cls.get_local_match_rgb(fit_arr, ref_arr, local_range)

        matched_img = Image.fromarray(matched_arr)
        return matched_img

    @no_type_check
    @staticmethod
    @njit(nogil=True, cache=True, fastmath=True)
    def get_local_match_l(
        fit_arr: np.ndarray, ref_arr: np.ndarray, local_range: int = 1
    ) -> np.ndarray:
        """Get locally palette-matched image array for an L image array.

        Arguments:
            fit_arr: Image array whose palette to fit to reference
            ref_arr: Image array whose palette to use as reference
            local_range: Range of adjacent pixels from which to draw best-fit color;
              1 checks a 3x3 window, 2 checks a 5x5 window, etc.
        Returns:
            Matched image array
        """
        scale = fit_arr.shape[0] // ref_arr.shape[0]
        matched_arr = np.zeros_like(fit_arr)
        dists = dict()  # noqa pylint: disable=use-dict-literal
        for fit_x in range(fit_arr.shape[0]):
            for fit_y in range(fit_arr.shape[1]):
                best_dist = -1.0
                best_color = 0

                ref_center = (fit_x // scale, fit_y // scale)
                for ref_x in range(
                    max(0, ref_center[0] - local_range),
                    min(ref_arr.shape[0] - 1, ref_center[0] + local_range) + 1,
                ):
                    for ref_y in range(
                        max(0, ref_center[1] - local_range),
                        min(ref_arr.shape[1] - 1, ref_center[1] + local_range) + 1,
                    ):
                        key = (fit_arr[fit_x, fit_y], ref_arr[ref_x, ref_y])
                        if key not in dists:
                            dists[key] = (
                                fit_arr[fit_x, fit_y] - ref_arr[ref_x, ref_y]
                            ) ** 2
                        dist = dists[key]
                        if best_dist < 0 or dist < best_dist:
                            best_dist = dist
                            best_color = ref_arr[ref_x, ref_y]
                matched_arr[fit_x, fit_y] = best_color
        return matched_arr

    @no_type_check
    @staticmethod
    @njit(nogil=True, cache=True, fastmath=True)
    def get_local_match_rgb(
        fit_arr: np.ndarray, ref_arr: np.ndarray, local_range: int = 1
    ) -> np.ndarray:
        """Get locally palette-matched image array for an RGB image array.

        Arguments:
            fit_arr: Image array whose palette to fit to reference
            ref_arr: Image array whose palette to use as reference
            local_range: Range of adjacent pixels from which to draw best-fit color;
              1 checks a 3x3 window, 2 checks a 5x5 window, etc.
        Returns:
            Matched image array
        """
        scale = fit_arr.shape[0] // ref_arr.shape[0]
        matched_arr = np.zeros_like(fit_arr)
        dists = dict()  # noqa pylint: disable=use-dict-literal
        for fit_x in range(fit_arr.shape[0]):
            for fit_y in range(fit_arr.shape[1]):
                best_dist = -1.0
                best_color = np.array([0, 0, 0], np.uint8)

                ref_center = (fit_x // scale, fit_y // scale)
                for ref_x in range(
                    max(0, ref_center[0] - local_range),
                    min(ref_arr.shape[0] - 1, ref_center[0] + local_range) + 1,
                ):
                    for ref_y in range(
                        max(0, ref_center[1] - local_range),
                        min(ref_arr.shape[1] - 1, ref_center[1] + local_range) + 1,
                    ):
                        key = (
                            fit_arr[fit_x, fit_y, 0],
                            fit_arr[fit_x, fit_y, 1],
                            fit_arr[fit_x, fit_y, 2],
                            ref_arr[ref_x, ref_y, 0],
                            ref_arr[ref_x, ref_y, 1],
                            ref_arr[ref_x, ref_y, 2],
                        )
                        if key not in dists:
                            dists[key] = get_perceptually_weighted_distance(
                                fit_arr[fit_x, fit_y], ref_arr[ref_x, ref_y]
                            )
                        dist = dists[key]
                        if best_dist < 0 or dist < best_dist:
                            best_dist = dist
                            best_color = ref_arr[ref_x, ref_y]
                matched_arr[fit_x, fit_y, :] = best_color
        return matched_arr
