#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaSplitter."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.core import AlphaMode, MaskFillMode
from pipescaler.image.operators.splitters import AlphaSplitter
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=AlphaSplitter,
    params=[
        {
            "alpha_mode": AlphaMode.GRAYSCALE,
            "mask_fill_mode": None,
        },
        {
            "alpha_mode": AlphaMode.MONOCHROME_OR_GRAYSCALE,
            "mask_fill_mode": None,
        },
        {
            "alpha_mode": AlphaMode.MONOCHROME_OR_GRAYSCALE,
            "mask_fill_mode": MaskFillMode.BASIC,
        },
        {
            "alpha_mode": AlphaMode.MONOCHROME_OR_GRAYSCALE,
            "mask_fill_mode": MaskFillMode.MATCH_PALETTE,
        },
    ],
)
def splitter(request: pytest.FixtureRequest) -> AlphaSplitter:
    """Pytest fixture that provides an AlphaSplitter instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured AlphaSplitter instance
    """
    return AlphaSplitter(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        xfail_unsupported_image_mode()("1"),
        xfail_unsupported_image_mode()("L"),
        "LA",
        xfail_unsupported_image_mode()("RGB"),
        "RGBA",
        "PLA",
        "PRGBA",
        "novel/RGBA_monochrome",
    ],
)
def test(input_filename: str, splitter: AlphaSplitter):
    """Test AlphaSplitter with various image modes containing alpha channels.

    Arguments:
        input_filename: Input image filename
        splitter: AlphaSplitter fixture instance
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    color_img, alpha_img = splitter(input_img)

    assert color_img.mode in splitter.outputs()["color"]
    assert color_img.mode == get_expected_output_mode(input_img).rstrip("A")
    assert color_img.size == input_img.size
    assert alpha_img.mode in splitter.outputs()["alpha"]
    assert alpha_img.size == input_img.size


@pytest.mark.parametrize("size", [(4, 1), (1, 4), (1, 1)])
@pytest.mark.parametrize(
    ("mode", "color_pixels"),
    [
        ("LA", [[11, 22, 33, 44]]),
        ("RGBA", [[(11, 21, 31), (12, 22, 32), (13, 23, 33), (14, 24, 34)]]),
    ],
)
def test_singleton_dimensions_preserve_color_pixels(
    size: tuple[int, int],
    mode: str,
    color_pixels: list[list[int | tuple[int, int, int]]],
):
    """Preserve spatial dimensions and color pixels when either axis is singleton.

    Arguments:
        size: Input image dimensions
        mode: Input image mode
        color_pixels: Expected color values across the four pixel slots
    """
    width, height = size
    image = Image.new(mode, size)
    for index in range(width * height):
        value = color_pixels[0][index]
        alpha = 101 + index
        if mode == "RGBA":
            assert isinstance(value, tuple)
            pixel = (*value, alpha)
        else:
            assert isinstance(value, int)
            pixel = (value, alpha)
        image.putpixel((index % width, index // width), pixel)

    color_image, alpha_image = AlphaSplitter()(image)

    assert color_image.size == size
    assert alpha_image.size == size
    expected_color = bytearray()
    if mode == "RGBA":
        for pixel in color_pixels[0][: width * height]:
            assert isinstance(pixel, tuple)
            expected_color.extend(pixel)
    else:
        for pixel in color_pixels[0][: width * height]:
            assert isinstance(pixel, int)
            expected_color.append(pixel)
    assert np.asarray(color_image).tobytes() == bytes(expected_color)
    assert np.asarray(alpha_image).tobytes() == bytes(
        101 + index for index in range(width * height)
    )


@pytest.mark.parametrize(
    "splitter",
    [
        AlphaSplitter(),
        AlphaSplitter(alpha_mode=AlphaMode.MONOCHROME_OR_GRAYSCALE),
        AlphaSplitter(
            alpha_mode=AlphaMode.MONOCHROME_OR_GRAYSCALE,
            mask_fill_mode=MaskFillMode.BASIC,
        ),
    ],
)
def test_repr_round_trip(splitter: AlphaSplitter):
    """Test AlphaSplitter repr round-trip recreation.

    Arguments:
        splitter: splitter
    """
    recreated = eval(repr(splitter))
    assert repr(recreated) == repr(splitter)
