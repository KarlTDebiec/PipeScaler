#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests palette matching against exact perceptual distance results."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
from PIL import Image
from scipy.spatial import KDTree

import pipescaler.image.utilities.palette_matcher as palette_module
from pipescaler.image.core.functions import get_palette
from pipescaler.image.utilities import PaletteMatcher


def test_dense_tree_search_avoids_allocating_candidate_lists(
    monkeypatch: pytest.MonkeyPatch,
):
    """Fall back to a compiled scan before dense neighbor lists consume memory.

    Arguments:
        monkeypatch: pytest patching fixture
    """

    class CountOnlyTree(KDTree):
        """Reject candidate-list allocation while permitting neighbor counts."""

        def query_ball_point(self, *args: Any, **kwargs: Any) -> np.ndarray:
            """Count neighbors without materializing candidate lists.

            Arguments:
                *args: tree query arguments
                **kwargs: tree query options
            Returns:
                number of candidates per query
            """
            assert kwargs.get("return_length") is True
            return super().query_ball_point(*args, **kwargs)

    monkeypatch.setattr(palette_module, "KDTree", CountOnlyTree)
    queries = np.zeros((513, 3), dtype=np.uint8)
    palette = np.full((2048, 3), 255, dtype=np.uint8)

    actual = PaletteMatcher.get_best_fit_palette(queries, palette)

    np.testing.assert_array_equal(actual, np.full_like(queries, 255))


def test_empty_query_palette_retains_shape():
    """Allow no colors to be queried without losing the RGB array shape."""
    actual = PaletteMatcher.get_best_fit_palette(
        np.empty((0, 3), dtype=np.uint8), np.array([[10, 20, 30]], dtype=np.uint8)
    )

    assert actual.shape == (0, 3)


def test_empty_reference_palette_is_rejected():
    """Reject an empty reference before entering the compiled search."""
    with pytest.raises(ValueError, match="at least one color"):
        PaletteMatcher.get_best_fit_palette(
            np.array([[10, 20, 30]], dtype=np.uint8), np.empty((0, 3), dtype=np.uint8)
        )


def test_get_best_fit_palette_breaks_ties_by_palette_order():
    """Keep the first palette color when weighted distances tie."""
    fit_palette = np.array([[10, 20, 30]], dtype=np.uint8)
    ref_palette = np.array([[10, 19, 30], [10, 21, 30]], dtype=np.uint8)

    best_fit_palette = PaletteMatcher.get_best_fit_palette(fit_palette, ref_palette)

    np.testing.assert_array_equal(best_fit_palette, [[10, 19, 30]])


def test_get_best_fit_palette_checks_colors_outside_nearby_cells():
    """Choose the true nearest palette color even when it is in a farther cell."""
    fit_palette = np.array([[31, 31, 31]], dtype=np.uint8)
    ref_palette = np.array([[15, 15, 15], [48, 31, 31]], dtype=np.uint8)

    best_fit_palette = PaletteMatcher.get_best_fit_palette(fit_palette, ref_palette)

    np.testing.assert_array_equal(best_fit_palette, [[48, 31, 31]])


def test_get_best_fit_palette_matches_brute_force_oracle():
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
        expected = _exhaustive_palette(fit_colors, palette)

        np.testing.assert_array_equal(actual, expected)


def test_tree_search_preserves_ties_and_exact_matches_across_batches():
    """Keep reference order for ties and exact colors across tree query batches."""
    palette = np.full((257, 3), 255, dtype=np.uint8)
    palette[:3] = [[128, 129, 128], [128, 127, 128], [0, 0, 0]]
    queries = np.tile(np.array([[128, 128, 128], [0, 0, 0]], dtype=np.uint8), (2050, 1))

    actual = PaletteMatcher.get_best_fit_palette(queries, palette)

    expected = np.tile(palette[[0, 2]], (2050, 1))
    np.testing.assert_array_equal(actual, expected)


def test_tree_search_uses_weighted_distance_after_filtering():
    """Choose the perceptual winner even when another color is nearer in the tree."""
    palette = np.zeros((2048, 3), dtype=np.uint8)
    palette[:2] = [[245, 100, 100], [255, 100, 111]]
    queries = np.tile(np.array([[255, 100, 100]], dtype=np.uint8), (513, 1))

    actual = PaletteMatcher.get_best_fit_palette(queries, palette)

    np.testing.assert_array_equal(actual, np.tile(palette[1], (513, 1)))


@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("size", [(1, 4), (4, 1), (1, 1), (5, 3)])
def test_run_preserves_pixel_mapping(mode: str, size: tuple[int, int]):
    """Map repeated pixels correctly without changing image dimensions.

    Arguments:
        mode: image mode to match
        size: target image dimensions
    """
    rng = np.random.default_rng(945)
    if mode == "L":
        reference = Image.fromarray(np.array([[10, 100, 240]], dtype=np.uint8))
        target = Image.fromarray(rng.integers(0, 256, size[::-1], dtype=np.uint8))
        palette = get_palette(reference)
        values = np.asarray(target).astype(float)
        expected = palette[np.abs(values[:, :, None] - palette).argmin(axis=2)]
    else:
        reference = Image.fromarray(
            np.array([[[10, 20, 30], [100, 150, 200], [240, 220, 200]]], dtype=np.uint8)
        )
        target = Image.fromarray(rng.integers(0, 256, (*size[::-1], 3), dtype=np.uint8))
        expected = _exhaustive_palette(
            np.asarray(target).reshape(-1, 3), get_palette(reference)
        ).reshape(*size[::-1], 3)

    actual = PaletteMatcher.run(reference, target)

    assert actual.size == size
    assert actual.mode == mode
    np.testing.assert_array_equal(np.asarray(actual), expected)


@pytest.mark.parametrize("distribution", ["uniform", "clustered", "separated"])
def test_tree_search_matches_exhaustive_distances(distribution: str):
    """Match an exhaustive oracle across uniform and difficult color distributions.

    Arguments:
        distribution: relationship between query and reference colors
    """
    rng = np.random.default_rng(964)
    if distribution == "uniform":
        queries = rng.integers(0, 256, (513, 3), dtype=np.uint8)
        palette = rng.integers(0, 256, (2048, 3), dtype=np.uint8)
    elif distribution == "clustered":
        queries = rng.integers(100, 110, (513, 3), dtype=np.uint8)
        palette = rng.integers(100, 110, (2048, 3), dtype=np.uint8)
    else:
        queries = rng.integers(0, 20, (513, 3), dtype=np.uint8)
        palette = rng.integers(230, 256, (2048, 3), dtype=np.uint8)

    actual = PaletteMatcher.get_best_fit_palette(queries, palette)

    np.testing.assert_array_equal(actual, _exhaustive_palette(queries, palette))


def _exhaustive_palette(queries: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Calculate independent exhaustive matches with bounded oracle memory.

    Arguments:
        queries: RGB colors to match
        palette: reference RGB colors in tie-breaking order
    Returns:
        closest reference colors by the existing weighted distance
    """
    matched = np.empty_like(queries)
    reference = palette.astype(float)
    for start in range(0, len(queries), 64):
        batch = queries[start : start + 64].astype(float)
        diff = batch[:, None, :] - reference[None, :, :]
        red_mean = (batch[:, None, 0] + reference[None, :, 0]) / 2
        distances = (
            (2 + red_mean / 256) * diff[:, :, 0] ** 2
            + 4 * diff[:, :, 1] ** 2
            + (2 + (255 - red_mean) / 256) * diff[:, :, 2] ** 2
        )
        matched[start : start + len(batch)] = palette[distances.argmin(axis=1)]
    return matched
