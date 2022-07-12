#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Functions for interacting with images."""
from __future__ import annotations

from typing import no_type_check

import numpy as np
from numba import njit
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import convolve

from pipescaler.common import validate_float
from pipescaler.core.exceptions import UnsupportedImageModeError


def convert_mode(image: Image.Image, mode: str) -> tuple[Image.Image, str]:
    """Convert image to specified mode, if necessary, returning image and original mode.

    Arguments:
        image: Image to convert
        mode: Mode to which to convert, if image is not already in mode
    Returns:
        Converted image, image's original mode
    """
    if image.mode != mode:
        return image.convert(mode), image.mode
    return image, image.mode


def crop_image(
    image: Image.Image, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0
) -> Image.Image:
    """Crop an image.

    TODO: Validate parameters

    Arguments:
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
    *,
    min_size: int = 1,
) -> Image.Image:
    """Expand an image by reflecting it around its edges.

    TODO: Implement option to tile rather than reflect

    Arguments:
        image: Input image
        left: Pixels to add to left side
        top: Pixels to add to top
        right: Pixels to add to right side
        bottom: Pixels to add to bottom
        min_size: Minimum size of expanded image
    Returns:
        Expanded image
    """
    transposed_horizontally = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    transposed_vertically = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    transposed_horizontally_and_vertically = transposed_horizontally.transpose(
        Image.Transpose.FLIP_TOP_BOTTOM
    )

    expanded = Image.new(
        image.mode,
        (
            max(min_size, left + image.size[0] + right),
            max(min_size, top + image.size[1] + bottom),
        ),
    )
    center = (expanded.size[0] // 2, expanded.size[1] // 2)

    expanded.paste(
        image, (center[0] - image.size[0] // 2, center[1] - image.size[1] // 2)
    )
    expanded.paste(
        transposed_horizontally,
        (center[0] + image.size[0] // 2, center[1] - image.size[1] // 2),
    )
    expanded.paste(
        transposed_horizontally,
        (
            center[0] - image.size[0] - image.size[0] // 2,
            center[1] - image.size[1] // 2,
        ),
    )
    expanded.paste(
        transposed_vertically,
        (
            center[0] - image.size[0] // 2,
            center[1] - image.size[1] - image.size[1] // 2,
        ),
    )
    expanded.paste(
        transposed_vertically,
        (center[0] - image.size[0] // 2, center[1] + image.size[1] // 2),
    )
    expanded.paste(
        transposed_horizontally_and_vertically,
        (
            center[0] + image.size[0] // 2,
            center[1] - image.size[1] - image.size[1] // 2,
        ),
    )
    expanded.paste(
        transposed_horizontally_and_vertically,
        (
            center[0] - image.size[0] - image.size[0] // 2,
            center[1] - image.size[1] - image.size[1] // 2,
        ),
    )
    expanded.paste(
        transposed_horizontally_and_vertically,
        (
            center[0] - image.size[0] - image.size[0] // 2,
            center[1] + image.size[1] // 2,
        ),
    )
    expanded.paste(
        transposed_horizontally_and_vertically,
        (center[0] + image.size[0] // 2, center[1] + image.size[1] // 2),
    )

    return expanded


def generate_normal_map_from_height_map_image(image: Image.Image) -> Image.Image:
    """Generate normal map image from a height map image.

    Arguments:
        image: Height map image
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


def get_palette(image: Image.Image) -> np.ndarray:
    """Get array of all colors present in an image.

    Arguments:
        image: Input image
    Returns:
        Array of all colors present in an image
    """
    return np.array([a[1] for a in image.getcolors(16581375)])


def get_font_size(
    text: str,
    width: int,
    height: int,
    proportional_height: float = 0.2,
    font: str = "Arial",
):
    """Get the font size at which text will take up defined portion of image's height.

    Arguments:
        text: Text to get size of
        width: Width of image
        height: Height of image
        proportional_height: Proportion of height which text should take up
        font: Font
    Returns:
        Font size at which text will take up proportional height of image
    """
    _, observed_height = get_text_size(text, width, height, font, 100)
    return round(100 / (observed_height / height) * proportional_height)


def get_text_size(
    text: str, width: int, height: int, font: str = "Arial", size: int = 100
) -> tuple[int, int]:
    """Get the size text would take up if drawn on an image.

    Arguments:
        text: Text to get size of
        width: width of image
        height: Height of image
        font: Font
        size: Font size
    Returns:
        Width and height of text
    """
    image = Image.new("L", (width, height))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(font, size)
    except OSError:
        font = ImageFont.truetype(font.lower(), size)
    return draw.textsize(text, font)


@no_type_check
@njit(nogil=True, cache=True, fastmath=True)
def get_perceptually_weighted_distance(
    color_1: np.ndarray, color_2: np.ndarray
) -> float:
    """Get the squared distance between two colors, adjusted for perception.

    Arguments:
        color_1: Color 1
        color_2: Color 2
    Returns:
        Squared distance between two colors
    """
    rmean = (color_1[0] + color_2[0]) / 2
    dr = color_1[0] - color_2[0]
    dg = color_1[1] - color_2[1]
    db = color_1[2] - color_2[2]
    return (
        ((2 + (rmean / 256)) * (dr**2))
        + (4 * (dg**2))
        + ((2 + ((255 - rmean) / 256)) * (db**2))
    )


def hstack_images(*images: Image.Image) -> Image.Image:
    """Horizontally stack images; rescaled to size of first image.

    Arguments:
        *images: Images to stack
    Returns:
        Horizontally stacked images
    """
    size = images[0].size
    stacked = Image.new("RGBA", (size[0] * len(images), size[1]))
    for i, image in enumerate(images):
        if image.size == size:
            stacked.paste(image, (size[0] * i, 0))
        else:
            stacked.paste(image.resize(size, resample=Image.NEAREST), (size[0] * i, 0))
    return stacked


def is_monochrome(
    image: Image.Image, mean_threshold: float = 0.01, proportion_threshold: float = 0.01
) -> bool:
    """Check whether a grayscale image contains only pure black and white.

    Arguments:
        image: Image to check
        mean_threshold: Threshold which mean difference between image and true
          monochrome must be below
        proportion_threshold: Threshold which percent of different pixels between image
          and true monochrome must be below
    Returns:
        Whether image contains only pure black and white
    """
    if image.mode != "L":
        raise UnsupportedImageModeError()
    mean_threshold = validate_float(mean_threshold, 0, 255)
    proportion_threshold = validate_float(proportion_threshold, 0, 1)

    l_array = np.array(image)
    one_array = np.array(image.convert("1").convert("L"))
    diff = np.abs(l_array - one_array)
    mean_diff = diff.mean()
    proportion_diff = (diff != 0).sum() / diff.size

    if mean_diff <= mean_threshold and proportion_diff <= proportion_threshold:
        return True
    return False


def label_image(image: Image.Image, text: str, font: str = "Arial") -> Image.Image:
    """Label an image in its upper left corner.

    Arguments:
        image: Image to label
        text: Text with which to label image
        font: Font with which to draw text
    Returns:
        Labeled image
    """
    labeled_image = image.copy()

    size = get_font_size(text, image.width, image.height, font=font)
    try:
        font = ImageFont.truetype(font, size)
    except OSError:
        font = ImageFont.truetype(font.lower(), size)

    ImageDraw.Draw(labeled_image).text(
        (
            round(image.width * 0.025),
            round(image.height * 0.025),
        ),
        text,
        font=font,
        stroke="white",
        stroke_fill="black",
        stroke_width=2,
    )

    return labeled_image


def remove_palette(image: Image.Image) -> Image.Image:
    """Remove palette from a paletted image.

    Arguments:
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
        array = np.array(image)
        fully_transparent_colors = set(
            np.where(np.array(list(image.info["transparency"])) == 0)[0]
        )
        pixels_per_non_grayscale_color = np.array(
            [
                (array == color).sum()
                for color in non_grayscale_colors - fully_transparent_colors
            ]
        )
        if pixels_per_non_grayscale_color.sum() == 0:
            return image.convert("RGBA").convert("LA")
        return image.convert("RGBA")
    if len(non_grayscale_colors) == 0:
        return image.convert("L")
    return image.convert("RGB")


def smooth_image(image: Image.Image, sigma: float) -> Image.Image:
    """Smooth an image using a Gaussian kernel.

    Arguments:
        image: Image to smooth
        sigma: Sigma of Gaussian with which to smooth
    Returns:
        Smoothed image
    """
    kernel = np.exp(
        (-1 * (np.arange(-3 * sigma, 3 * sigma + 1).astype(float) ** 2))
        / (2 * (sigma**2))
    )
    smoothed_array = np.array(image).astype(float)
    smoothed_array = convolve(smoothed_array, kernel[np.newaxis])
    smoothed_array = convolve(smoothed_array, kernel[np.newaxis].T)
    smoothed_array = np.clip(smoothed_array, 0, 255).astype(np.uint8)
    smoothed = Image.fromarray(smoothed_array)

    return smoothed


def vstack_images(*images: Image.Image) -> Image.Image:
    """Vertically stack images; rescaled to size of first image.

    Arguments:
        *images: Images to stack
    Returns:
        Vertically stacked images
    """
    size = images[0].size
    stacked = Image.new("RGBA", (size[0], size[1] * len(images)))
    for i, image in enumerate(images):
        if image.size == size:
            stacked.paste(image, (0, size[1] * i))
        else:
            stacked.paste(image.resize(size, resample=Image.NEAREST), (0, size[1] * i))
    return stacked
