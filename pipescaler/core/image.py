#!/usr/bin/env python
#   pipescaler/core/image.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Core pipescaler functions for interacting with images"""
from __future__ import annotations

import numpy as np
from PIL import Image
from scipy.ndimage import convolve


def crop_image(
    image: Image.Image, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0
) -> Image.Image:
    """
    Crop an image.

    TODO: Validate

    Args:
        image: Input image
        left: Pixels to remove from left side
        top: Pixels to remove from top
        right: Pixels to remove from right side
        bottom: Pixels to remove from bottom

    Returns:
        Cropped Image
    """
    cropped = image.crop((left, top, image.size[0] - right, image.size[1] - bottom))

    return cropped


def expand_image(
    image: Image.Image,
    left: int = 0,
    top: int = 0,
    right: int = 0,
    bottom: int = 0,
    min_size: int = 1,
) -> Image.Image:
    """
    Expand an image by reflecting it around its edges.

    TODO: Option to tile rather than reflect

    Args:
        image: Input image
        left: Pixels to remove from left side
        top: Pixels to remove from top
        right: Pixels to remove from right side
        bottom: Pixels to remove from bottom
        min_size: Minimum size of expanded image

    Returns:
        Expanded image
    """
    w, h = image.size
    new_w = max(min_size, left + w + right)
    new_h = max(min_size, top + h + bottom)

    transposed_h = image.transpose(Image.FLIP_LEFT_RIGHT)
    transposed_v = image.transpose(Image.FLIP_TOP_BOTTOM)
    transposed_hv = transposed_h.transpose(Image.FLIP_TOP_BOTTOM)

    expanded = Image.new(image.mode, (new_w, new_h))
    x = expanded.size[0] // 2
    y = expanded.size[1] // 2
    expanded.paste(image, (x - w // 2, y - h // 2))
    expanded.paste(transposed_h, (x + w // 2, y - h // 2))
    expanded.paste(transposed_h, (x - w - w // 2, y - h // 2))
    expanded.paste(transposed_v, (x - w // 2, y - h - h // 2))
    expanded.paste(transposed_v, (x - w // 2, y + h // 2))
    expanded.paste(transposed_hv, (x + w // 2, y - h - h // 2))
    expanded.paste(transposed_hv, (x - w - w // 2, y - h - h // 2))
    expanded.paste(transposed_hv, (x - w - w // 2, y + h // 2))
    expanded.paste(transposed_hv, (x + w // 2, y + h // 2))

    return expanded


def generate_normal_map_from_height_map_image(image: Image.Image) -> Image.Image:
    """
    Generates normal map image from a height map image.

    Args:
        image: Height map image from which to generate normal map

    Returns:
        Normal map image
    """
    input_array = np.array(image)

    # Prepare normal map
    kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    gradient_x = convolve(input_array.astype(float), kernel)
    gradient_y = convolve(input_array.astype(float), kernel.T)
    output_array = np.zeros((input_array.shape[0], input_array.shape[1], 3))
    max_dimension = max(gradient_x.max(), gradient_y.max())
    output_array[..., 0] = gradient_x / max_dimension
    output_array[..., 1] = gradient_y / max_dimension
    output_array[..., 2] = 1

    # Normalize
    magnitude = np.sqrt(
        output_array[..., 0] ** 2
        + output_array[..., 1] ** 2
        + output_array[..., 2] ** 2
    )
    output_array[..., 0] /= magnitude
    output_array[..., 1] /= magnitude
    output_array[..., 2] /= magnitude

    # Convert to image
    output_array = ((output_array * 0.5) + 0.5) * 255
    output_array = np.clip(output_array, 0, 255).astype(np.uint8)
    output_image = Image.fromarray(output_array)

    return output_image


def remove_palette_from_image(image: Image.Image) -> Image.Image:
    """
    Remove palette from a paletted image.

    Args:
        image: Image in 'P' mode

    Returns:
        Image in 'L', 'LA', 'RGB', or 'RGBA' mode
    """
    palette = np.reshape(image.getpalette(), (-1, 3))
    non_grayscale_colors = set(
        np.where(
            np.logical_or(
                palette[:, 0] != palette[:, 1], palette[:, 1] != palette[:, 2]
            )
        )[0]
    )
    if "transparency" in image.info:
        datum = np.array(image)
        fully_transparent_colors = set(
            np.where(np.array(list(image.info["transparency"])) == 0)[0]
        )
        pixels_per_non_grayscale_color = np.array(
            [
                (datum == color).sum()
                for color in non_grayscale_colors - fully_transparent_colors
            ]
        )
        if pixels_per_non_grayscale_color.sum() == 0:
            return image.convert("RGBA").convert("LA")
        else:
            return image.convert("RGBA")
    elif len(non_grayscale_colors) == 0:
        return image.convert("L")
    else:
        return image.convert("RGB")


def smooth_image(image: Image.Image, sigma: float):
    """
    Smooth an image using a Gaussian kernel.

    Args:
        image: Image to smooth
        sigma: Sigma of Gaussian with which to smooth

    Returns:
        Smoothed image
    """
    kernel = np.exp(
        (-1 * (np.arange(-3 * sigma, 3 * sigma + 1).astype(float) ** 2))
        / (2 * (sigma ** 2))
    )
    smoothed_array = np.array(image).astype(float)
    smoothed_array = convolve(smoothed_array, kernel[np.newaxis])
    smoothed_array = convolve(smoothed_array, kernel[np.newaxis].T)
    smoothed_array = np.clip(smoothed_array, 0, 255).astype(np.uint8)
    smoothed = Image.fromarray(smoothed_array)

    return smoothed
