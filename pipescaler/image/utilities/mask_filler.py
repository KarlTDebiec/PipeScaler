#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Erases masked pixels within an image."""

from __future__ import annotations

from logging import warning

import numpy as np
from PIL import Image

from pipescaler.core import Utility
from pipescaler.image.core.enums import MaskFillMode
from pipescaler.image.core.exceptions import UnsupportedImageModeError

from .mask_shader_filler import MaskShaderError, MaskShaderFiller
from .palette_matcher import PaletteMatcher

__all__ = ["MaskFiller"]


class MaskFiller(Utility):
    """Erase masked pixels, preferring WGSL for substantial masked regions.

    Masks below 1,024 masked pixels use the CPU to avoid dispatch overhead.
    Larger masks use cached compute pipelines and fall back to the CPU if the
    graphics runtime fails. The first GPU fill also initializes the runtime.
    """

    _minimum_shader_pixels = 1024
    """Minimum masked-pixel count before attempting GPU execution."""

    @classmethod
    def run(  # ty: ignore[invalid-method-override]
        cls, img: Image.Image, mask: Image.Image, mask_fill_mode: MaskFillMode
    ) -> Image.Image:
        """Erases masked pixels within an image.

        Each round fills only pixels with the highest unmasked-neighbor count,
        using integer averages from the previous round's 3x3 neighborhoods.
        Fully masked images remain unchanged because no color can propagate.

        Arguments:
            img: image whose mode must be L or RGB
            mask: same-sized mode 1 mask; white pixels are masked
            mask_fill_mode: whether to match filled colors to the original palette
        Returns:
            image with masked pixels replaced
        Raises:
            UnsupportedImageModeError: if the image or mask mode is unsupported
            ValueError: if image and mask sizes differ
        """
        if img.mode not in {"L", "RGB"} or mask.mode != "1":
            raise UnsupportedImageModeError(
                "Mask filling requires an L or RGB image and a mode 1 mask; "
                f"received '{img.mode}' and '{mask.mode}'"
            )
        if img.size != mask.size:
            raise ValueError("Mask filling requires matching image and mask sizes")
        mask_arr = np.asarray(mask)
        masked_count = int(np.count_nonzero(mask_arr))
        if masked_count in {0, mask_arr.size}:
            return img.copy()

        filled_img = None
        if masked_count >= cls._minimum_shader_pixels:
            try:
                filled_img = MaskShaderFiller.run(img, mask)
            except MaskShaderError as exc:
                warning(
                    f"{cls.__name__}: Shader path unavailable ('{exc}'); "
                    "falling back to CPU mask filling."
                )

        if filled_img is None:
            image_arr = np.array(img)
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
        if count == 0:
            return image_arr, set(), opaque_neighbor_counts, set()
        pixels_to_fill_next_iter = set()
        pixels_to_recount_next_iter = set()
        for pixel in pixels_to_fill:
            if opaque_neighbor_counts[pixel] == count:
                color = np.zeros_like(image_arr[pixel[0], pixel[1]], dtype=np.uint32)
                for x_p in range(max(0, pixel[0] - 1), min(width, pixel[0] + 2)):
                    for y_p in range(max(0, pixel[1] - 1), min(height, pixel[1] + 2)):
                        pixel_p = (x_p, y_p)
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
