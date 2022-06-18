#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Matches the palette of one image to another, restricted to nearby colors."""
from typing import no_type_check

import numpy as np
from numba import njit
from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core import Utility
from pipescaler.core.exceptions import UnsupportedImageModeError
from pipescaler.core.image import get_perceptually_weighted_distance


class LocalPaletteMatcher(Utility):
    """Matches the palette of one image to another, restricted to nearby colors."""

    def __init__(self, local_range: int = 1):
        """Validate and store configuration and initialize.

        Arguments:
            local_range: Range of adjacent pixels from which to draw best-fit color;
              1 checks a 3x3 window, 2 checks a 5x5 window, etc.
        """
        self.local_range = validate_int(local_range, min_value=1)

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
        ref_array = np.array(ref_image)
        fit_array = np.array(fit_image)

        if fit_image.mode == "L":
            matched_array = self.get_local_match_l(
                fit_array, ref_array, self.local_range
            )
        else:
            matched_array = self.get_local_match_rgb(
                fit_array, ref_array, self.local_range
            )

        matched_image = Image.fromarray(matched_array)
        return matched_image

    @no_type_check
    @staticmethod
    @njit(nogil=True, cache=True, fastmath=True)
    def get_local_match_l(
        fit_array: np.ndarray, ref_array: np.ndarray, local_range: int = 1
    ) -> np.ndarray:
        """Get locally palette-matched image array for an L image array.

        Arguments:
            fit_array: Image array whose palette to fit to reference
            ref_array: Image array whose palette to use as reference
            local_range: Range of adjacent pixels from which to draw best-fit color;
              1 checks a 3x3 window, 2 checks a 5x5 window, etc.

        Returns:
            Matched imaged array
        """
        scale = fit_array.shape[0] // ref_array.shape[0]
        matched_array = np.zeros_like(fit_array)
        dists = dict()
        for fit_x in range(fit_array.shape[0]):
            for fit_y in range(fit_array.shape[1]):
                fit_color = fit_array[fit_x, fit_y]
                best_dist = -1.0
                best_color = 0

                ref_center_x = fit_x // scale
                ref_center_y = fit_y // scale
                for ref_x in range(
                    max(0, ref_center_x - local_range),
                    min(ref_array.shape[0] - 1, ref_center_x + local_range) + 1,
                ):
                    for ref_y in range(
                        max(0, ref_center_y - local_range),
                        min(ref_array.shape[1] - 1, ref_center_y + local_range) + 1,
                    ):
                        ref_color = ref_array[ref_x, ref_y]
                        key = (fit_color, ref_color)
                        if key not in dists:
                            dists[key] = (fit_color - ref_color) ** 2
                        dist = dists[key]
                        if best_dist < 0 or dist < best_dist:
                            best_dist = dist
                            best_color = ref_color
                matched_array[fit_x, fit_y] = best_color
        return matched_array

    @no_type_check
    @staticmethod
    @njit(nogil=True, cache=True, fastmath=True)
    def get_local_match_rgb(
        fit_array: np.ndarray, ref_array: np.ndarray, local_range: int = 1
    ) -> np.ndarray:
        """Get locally palette-matched image array for an RGB image array.

        Arguments:
            fit_array: Image array whose palette to fit to reference
            ref_array: Image array whose palette to use as reference
            local_range: Range of adjacent pixels from which to draw best-fit color;
              1 checks a 3x3 window, 2 checks a 5x5 window, etc.

        Returns:
            Matched imaged array
        """
        scale = fit_array.shape[0] // ref_array.shape[0]
        matched_array = np.zeros_like(fit_array)
        dists = dict()
        for fit_x in range(fit_array.shape[0]):
            for fit_y in range(fit_array.shape[1]):
                fit_color = fit_array[fit_x, fit_y]
                best_dist = -1.0
                best_color = np.array([0, 0, 0], np.uint8)

                ref_center_x = fit_x // scale
                ref_center_y = fit_y // scale
                for ref_x in range(
                    max(0, ref_center_x - local_range),
                    min(ref_array.shape[0] - 1, ref_center_x + local_range) + 1,
                ):
                    for ref_y in range(
                        max(0, ref_center_y - local_range),
                        min(ref_array.shape[1] - 1, ref_center_y + local_range) + 1,
                    ):
                        ref_color = ref_array[ref_x, ref_y]
                        key = (
                            fit_color[0],
                            fit_color[1],
                            fit_color[2],
                            ref_color[0],
                            ref_color[1],
                            ref_color[2],
                        )
                        if key not in dists:
                            dists[key] = get_perceptually_weighted_distance(
                                fit_color, ref_color
                            )
                        dist = dists[key]
                        if best_dist < 0 or dist < best_dist:
                            best_dist = dist
                            best_color = ref_color
                matched_array[fit_x, fit_y, :] = best_color
        return matched_array
