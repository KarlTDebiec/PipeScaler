#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Matches the palette of one image to another."""

from __future__ import annotations

from typing import no_type_check

import numpy as np
from numba import njit
from PIL import Image
from scipy.spatial import KDTree

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
        """Find exact nearest reference colors, keeping palette order for ties.

        Small searches scan the reference directly. Larger searches use a tree
        only to exclude colors that cannot win under the existing weighted metric.
        Dense candidate batches fall back to a scan to bound temporary memory.
        Arguments:
            fit_palette: 8-bit RGB colors to match
            ref_palette: reference 8-bit RGB colors in tie-breaking order
        Returns:
            nearest reference color for each input color
        Raises:
            ValueError: if the reference palette is empty
        """
        if len(ref_palette) == 0:
            raise ValueError("Reference palette must contain at least one color")
        # Avoid tree setup for searches with at most one million comparisons
        if len(fit_palette) * len(ref_palette) <= 1_048_576:
            return _match_palette(fit_palette, ref_palette)

        # The squared tree distance L = 2*dr**2 + 4*dg**2 + 2*db**2 satisfies
        # L <= weighted_distance <= 1.5*L for 8-bit RGB colors
        weights = np.array([np.sqrt(2), 2, np.sqrt(2)])
        tree = KDTree(ref_palette.astype(float) * weights)
        matched = np.empty_like(fit_palette)
        for start in range(0, len(fit_palette), 4096):
            batch = fit_palette[start : start + 4096]
            points = batch.astype(float) * weights
            nearest_distances, _ = tree.query(points)
            # A nearest tree neighbor gives an upper bound on the winning distance;
            # include boundary ties despite floating-point rounding in the tree
            radii = nearest_distances * np.sqrt(1.5) + 1e-10
            counts = tree.query_ball_point(points, radii, return_length=True)
            # Count first so dense batches cannot allocate unbounded neighbor lists
            if counts.sum() > 262_144:
                result = _match_palette(batch, ref_palette)
            else:
                candidates = tree.query_ball_point(points, radii, return_sorted=True)
                offsets = np.concatenate(([0], np.cumsum(counts)))
                indices = np.concatenate(candidates).astype(np.int64)
                result = _match_candidates(batch, ref_palette, indices, offsets)
            matched[start : start + len(batch)] = result
        return matched

    @classmethod
    def run(  # ty: ignore[invalid-method-override]
        cls, ref_img: Image.Image, fit_img: Image.Image
    ) -> Image.Image:
        """Match the palette of an image to a reference.

        Arguments:
            ref_img: image whose palette to use as reference
            fit_img: image whose palette to fit to reference
        Returns:
            image with palette fit to reference
        Raises:
            UnsupportedImageModeError: if image modes differ or are unsupported
        """
        if ref_img.mode != fit_img.mode or fit_img.mode not in {"L", "RGB"}:
            raise UnsupportedImageModeError(
                "Palette matching requires matching L or RGB modes; "
                f"received reference '{ref_img.mode}' and target '{fit_img.mode}'"
            )
        ref_palette = get_palette(ref_img).astype(np.uint8)
        fit_arr = np.asarray(fit_img)
        if fit_img.mode == "L":
            fit_palette, inverse = np.unique(fit_arr, return_inverse=True)
            distances = (
                ref_palette.astype(float) - fit_palette.astype(float)[:, None]
            ) ** 2
            best_fit_palette = ref_palette[distances.argmin(axis=1)]
            matched_arr = best_fit_palette[inverse].reshape(fit_arr.shape)
        else:
            # Pack RGB values so unique/inverse indexing avoids per-pixel Python work
            channels = fit_arr.astype(np.uint32)
            packed = (
                (channels[:, :, 0] << 16) | (channels[:, :, 1] << 8) | channels[:, :, 2]
            )
            colors, inverse = np.unique(packed, return_inverse=True)
            fit_palette = np.stack(
                (colors >> 16, (colors >> 8) & 255, colors & 255), axis=-1
            ).astype(np.uint8)
            best_fit_palette = cls.get_best_fit_palette(fit_palette, ref_palette)
            matched_arr = best_fit_palette[inverse].reshape(fit_arr.shape)
        return Image.fromarray(matched_arr)


@no_type_check
@njit(nogil=True, cache=True)
def _match_candidates(
    queries: np.ndarray, palette: np.ndarray, indices: np.ndarray, offsets: np.ndarray
) -> np.ndarray:
    """Select the exact nearest color from each ordered tree candidate list.

    Arguments:
        queries: RGB colors to match
        palette: reference RGB colors
        indices: flattened candidate indices in reference-palette order
        offsets: start and end offsets for each query's candidates
    Returns:
        nearest reference color for each query
    """
    matched = np.empty_like(queries)
    for i in range(len(queries)):
        best = indices[offsets[i]]
        best_distance = get_perceptually_weighted_distance(queries[i], palette[best])
        for position in range(offsets[i] + 1, offsets[i + 1]):
            candidate = indices[position]
            distance = get_perceptually_weighted_distance(
                queries[i], palette[candidate]
            )
            if distance < best_distance:
                best = candidate
                best_distance = distance
        matched[i] = palette[best]
    return matched


@no_type_check
@njit(nogil=True, cache=True)
def _match_palette(queries: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Scan a complete reference palette in one compiled call.

    Arguments:
        queries: RGB colors to match
        palette: non-empty reference RGB colors in tie-breaking order
    Returns:
        nearest reference color for each query
    """
    matched = np.empty_like(queries)
    for i in range(len(queries)):
        best = 0
        best_distance = get_perceptually_weighted_distance(queries[i], palette[0])
        for candidate in range(1, len(palette)):
            if best_distance == 0:
                break
            distance = get_perceptually_weighted_distance(
                queries[i], palette[candidate]
            )
            if distance < best_distance:
                best = candidate
                best_distance = distance
        matched[i] = palette[best]
    return matched
