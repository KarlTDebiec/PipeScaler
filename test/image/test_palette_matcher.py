#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests palette matching against exact perceptual distance results."""

from __future__ import annotations

import numpy as np

from pipescaler.image.utilities import PaletteMatcher


def _weighted_distance(color_1: np.ndarray, color_2: np.ndarray) -> float:
    """Calculate the palette matcher's weighted RGB distance.

    Arguments:
        color_1: First RGB color
        color_2: Second RGB color
    Returns:
        Squared perceptual distance
    """
    rmean = (float(color_1[0]) + float(color_2[0])) / 2
    dr, dg, db = color_1.astype(float) - color_2.astype(float)
    return (2 + rmean / 256) * dr**2 + 4 * dg**2 + (2 + (255 - rmean) / 256) * db**2


def _brute_force_best_fit(color: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Return the first palette color at the minimum weighted distance.

    Arguments:
        color: RGB color to match
        palette: Candidate RGB colors
    Returns:
        Closest color from the palette
    """
    return min(palette, key=lambda candidate: _weighted_distance(color, candidate))


def test_get_best_fit_palette_checks_colors_outside_nearby_cells() -> None:
    """Choose the true nearest palette color even when it is in a farther cell."""
    fit_palette = np.array([[31, 31, 31]], dtype=np.uint8)
    ref_palette = np.array([[15, 15, 15], [48, 31, 31]], dtype=np.uint8)

    best_fit_palette = PaletteMatcher.get_best_fit_palette(fit_palette, ref_palette)

    np.testing.assert_array_equal(best_fit_palette, [[48, 31, 31]])


def test_get_best_fit_palette_matches_brute_force_oracle() -> None:
    """Match multiple palettes and colors to a brute-force metric oracle."""
    palettes = [
        np.array([[15, 15, 15], [48, 31, 31]], dtype=np.uint8),
        np.array(
            [[0, 0, 0], [255, 255, 255], [255, 0, 0], [0, 255, 255]],
            dtype=np.uint8,
        ),
        np.array(
            [[20, 2, 220], [25, 80, 40], [200, 70, 15], [130, 180, 210]],
            dtype=np.uint8,
        ),
    ]
    fit_colors = np.array(
        [[31, 31, 31], [80, 90, 100], [240, 40, 210], [128, 128, 128]],
        dtype=np.uint8,
    )

    for palette in palettes:
        actual = PaletteMatcher.get_best_fit_palette(fit_colors, palette)
        expected = np.array(
            [_brute_force_best_fit(color, palette) for color in fit_colors]
        )

        np.testing.assert_array_equal(actual, expected)


def test_get_best_fit_palette_breaks_ties_by_palette_order() -> None:
    """Keep the first palette color when weighted distances tie."""
    fit_palette = np.array([[10, 20, 30]], dtype=np.uint8)
    ref_palette = np.array([[10, 19, 30], [10, 21, 30]], dtype=np.uint8)

    best_fit_palette = PaletteMatcher.get_best_fit_palette(fit_palette, ref_palette)

    np.testing.assert_array_equal(best_fit_palette, [[10, 19, 30]])
