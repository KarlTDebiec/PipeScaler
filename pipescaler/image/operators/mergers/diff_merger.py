#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges two images into a perceptually weighted blue-black-red diff image."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

from pipescaler.image.core.numba import get_perceptually_weighted_distance
from pipescaler.image.core.operators import ImageMerger
from pipescaler.image.core.validation import validate_image

if TYPE_CHECKING:
    from pipescaler.image.core.typing import ImageMode


class DiffMerger(ImageMerger):
    """Merges two images into a perceptually weighted blue-black-red diff image."""

    def __call__(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            input_images: Input images
        Returns:
            Merged output image
        """
        first_img = validate_image(input_images[0], self.inputs()["first"])
        second_img = validate_image(input_images[1], self.inputs()["second"])

        if first_img.mode != second_img.mode:
            raise ValueError(
                f"Input image modes must match: '{first_img.mode}' != "
                f"'{second_img.mode}'"
            )

        first_img, second_img = self._resize_to_shared_size(first_img, second_img)
        first_arr = np.array(first_img)
        second_arr = np.array(second_img)

        if first_img.mode == "L":
            first_rgb = np.stack((first_arr, first_arr, first_arr), axis=-1)
            second_rgb = np.stack((second_arr, second_arr, second_arr), axis=-1)
            signed_delta = second_arr.astype(float) - first_arr.astype(float)
        else:
            first_rgb = first_arr
            second_rgb = second_arr
            signed_delta = np.mean(
                second_arr.astype(float) - first_arr.astype(float), axis=2
            )

        magnitude = self._get_perceptual_magnitude(first_rgb, second_rgb)
        output_arr = np.zeros((*magnitude.shape, 3), np.uint8)

        red_mask = signed_delta >= 0
        blue_mask = ~red_mask

        output_arr[:, :, 0][red_mask] = magnitude[red_mask]
        output_arr[:, :, 2][blue_mask] = magnitude[blue_mask]

        return Image.fromarray(output_arr, mode="RGB")

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator."""
        return {
            "first": ("L", "RGB"),
            "second": ("L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("RGB",),
        }

    @classmethod
    def _get_perceptual_magnitude(
        cls, first_rgb: np.ndarray, second_rgb: np.ndarray
    ) -> np.ndarray:
        """Calculate normalized perceptual difference magnitudes for each pixel.

        Arguments:
            first_rgb: First input image as rgb array
            second_rgb: Second input image as rgb array
        Returns:
            Per-pixel perceptual magnitudes in range 0-255
        """
        max_distance = get_perceptually_weighted_distance(
            np.array([0.0, 0.0, 0.0]), np.array([255.0, 255.0, 255.0])
        )

        flat_first = first_rgb.reshape(-1, 3).astype(float)
        flat_second = second_rgb.reshape(-1, 3).astype(float)
        flat_magnitude = np.zeros(flat_first.shape[0], dtype=float)

        for i in range(flat_first.shape[0]):
            flat_magnitude[i] = get_perceptually_weighted_distance(
                flat_first[i], flat_second[i]
            )

        magnitude = np.sqrt(flat_magnitude / max_distance)
        return (
            np.round(np.clip(magnitude * 255.0, 0, 255))
            .astype(np.uint8)
            .reshape(first_rgb.shape[:2])
        )

    @classmethod
    def _resize_to_shared_size(
        cls, first_img: Image.Image, second_img: Image.Image
    ) -> tuple[Image.Image, Image.Image]:
        """Resize smaller image to larger image size if aspect ratios match.

        Arguments:
            first_img: First input image
            second_img: Second input image
        Returns:
            Images with matching sizes
        """
        first_ratio = first_img.width / first_img.height
        second_ratio = second_img.width / second_img.height
        if not np.isclose(first_ratio, second_ratio):
            raise ValueError(
                "Input image aspect ratios must match: "
                f"{first_img.width}x{first_img.height} != "
                f"{second_img.width}x{second_img.height}"
            )
        if first_img.size == second_img.size:
            return first_img, second_img

        if first_img.width * first_img.height >= second_img.width * second_img.height:
            return first_img, second_img.resize(first_img.size, resample=Image.NEAREST)
        return first_img.resize(second_img.size, resample=Image.NEAREST), second_img
