#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Erases masked pixels within an image."""

from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.core import Utility
from pipescaler.image.core.enums import MaskFillMode

from .palette_matcher import PaletteMatcher


class MaskFiller(Utility):
    """Erases masked pixels within an image."""

    @classmethod
    def run(
        cls, img: Image.Image, mask: Image.Image, mask_fill_mode: MaskFillMode
    ) -> Image.Image:
        """Erases masked pixels within an image.

        Each erased pixel is replaced with the average color of adjacent unmasked
        pixels, iteratively.

        Arguments:
            img: Image; mode must be RGB
            mask: Mask; mode must be 1; white (True) pixels are masked
            mask_fill_mode: Mask fill mode
        Returns:
            Image with masked pixels replaced
        """
        image_arr = np.array(img)
        mask_arr = np.array(mask)

        # Get all pixels to be filled
        pixels_to_fill = set()
        for x in range(mask_arr.shape[0]):
            for y in range(mask_arr.shape[1]):
                if mask_arr[x, y]:
                    pixels_to_fill.add((x, y))

        # Iterate until no pixels remain to be filled
        opaque_neighbor_counts: dict[tuple[int, int], int] = {}
        pixels_to_recount = pixels_to_fill.copy()
        while len(pixels_to_fill) > 0:
            (
                image_arr,
                pixels_to_fill,
                opaque_neighbor_counts,
                pixels_to_recount,
            ) = cls.run_iteration(
                image_arr, pixels_to_fill, opaque_neighbor_counts, pixels_to_recount
            )

        # Return image
        filled_img = Image.fromarray(image_arr)
        if mask_fill_mode == MaskFillMode.MATCH_PALETTE:
            filled_img = PaletteMatcher.run(img, filled_img)
        return filled_img

    @staticmethod
    def run_iteration(
        image_arr: np.ndarray,
        pixels_to_fill: set[tuple[int, int]],
        opaque_neighbor_counts: dict[tuple[int, int], int],
        pixels_to_recount: set[tuple[int, int]],
    ) -> tuple[
        np.ndarray,
        set[tuple[int, int]],
        dict[tuple[int, int], int],
        set[tuple[int, int]],
    ]:
        """Fills pixels whose number of opaque neighbors is equal to the max.

        Arguments:
            image_arr: Image array
            pixels_to_fill: Pixels that remain to be filled
            opaque_neighbor_counts: Number of opaque neighbors of each pixel to fill
            pixels_to_recount: Pixels whose opaque neighbor counts need to be updated
        Returns:
            Updated image array, pixels to fill, opaque neighbor counts, and pixels to
            recount
        """
        width = image_arr.shape[0]
        height = image_arr.shape[1]

        # Count number of opaque pixels adjacent to each pixel to be filled
        for pixel in pixels_to_recount:
            count = 0
            for x_p in range(max(0, pixel[0] - 1), min(width, pixel[0] + 2)):
                for y_p in range(max(0, pixel[1] - 1), min(height, pixel[1] + 2)):
                    if (x_p, y_p) not in pixels_to_fill:
                        count += 1
            opaque_neighbor_counts[pixel] = count

        count = max(opaque_neighbor_counts.values())
        pixels_to_fill_next_iter = set()
        pixels_to_recount_next_iter = set()
        for pixel in pixels_to_fill:
            if opaque_neighbor_counts[pixel] == count:
                color = np.zeros(3, dtype=np.uint32)
                for x_p in range(max(0, pixel[0] - 1), min(width, pixel[0] + 2)):
                    for y_p in range(max(0, pixel[1] - 1), min(height, pixel[1] + 2)):
                        pixel_p = (x_p, y_p)
                        if pixel_p == pixel:
                            continue
                        if pixel_p not in pixels_to_fill:
                            color += image_arr[x_p, y_p]
                        elif (
                            pixel_p in opaque_neighbor_counts
                            and opaque_neighbor_counts[pixel_p] != count
                        ):
                            pixels_to_recount_next_iter.add(pixel_p)
                image_arr[pixel[0], pixel[1]] = color // count
                opaque_neighbor_counts.pop(pixel)
            else:
                pixels_to_fill_next_iter.add(pixel)

        return (
            image_arr,
            pixels_to_fill_next_iter,
            opaque_neighbor_counts,
            pixels_to_recount_next_iter,
        )
