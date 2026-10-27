#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ModeProcessor."""

from __future__ import annotations

from typing import Any, Literal, cast

import pytest
from PIL import Image

from pipescaler.image.operators.processors import ModeProcessor
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=ModeProcessor,
    params=[
        {"mode": "1"},
        {"mode": "L"},
        {"mode": "LA"},
        {"mode": "RGB"},
        {"mode": "RGBA"},
    ],
)
def processor(request: pytest.FixtureRequest) -> ModeProcessor:
    """Pytest fixture that provides a ModeProcessor instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured ModeProcessor instance
    """
    return ModeProcessor(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        "1",
        "L",
        "LA",
        "RGB",
        "RGBA",
        "PL",
        "PLA",
        "PRGB",
        "PRGBA",
    ],
)
def test(input_filename: str, processor: ModeProcessor):
    """Test ModeProcessor with various image modes.

    Arguments:
        input_filename: Input image filename
        processor: ModeProcessor fixture instance
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.size == input_img.size
    assert output_img.mode == processor.mode


def test_invalid_mode():
    """Test ModeProcessor with unsupported output mode."""
    with pytest.raises(ValueError, match="not one of options"):
        ModeProcessor(mode=cast("Any", "HSV"))


@pytest.mark.parametrize(
    ("input_image", "output_mode", "expected"),
    [
        (Image.new("RGBA", (1, 1), (255, 0, 0, 0)), "RGB", (255, 255, 255)),
        (Image.new("RGBA", (1, 1), (255, 0, 0, 128)), "RGB", (255, 127, 127)),
        (Image.new("RGBA", (1, 1), (255, 0, 0, 255)), "RGB", (255, 0, 0)),
        (Image.new("RGBA", (1, 1), (255, 0, 0, 0)), "L", 255),
        (Image.new("LA", (1, 1), (200, 0)), "L", 255),
        (Image.new("LA", (1, 1), (200, 128)), "L", 227),
        (Image.new("LA", (1, 1), (200, 255)), "L", 200),
    ],
)
def test_alpha_is_composited_before_removal(
    input_image: Image.Image,
    output_mode: Literal["RGB", "L"],
    expected: int | tuple[int, int, int],
):
    """Composite transparent inputs over the configured background before conversion.

    Arguments:
        input_image: input image with optional alpha
        output_mode: output mode without alpha
        expected: expected pixel value after conversion
    """
    output_image = ModeProcessor(mode=output_mode, background_color="#ffffff")(
        input_image
    )

    assert output_image.mode == output_mode
    assert output_image.getpixel((0, 0)) == expected


def test_palette_transparency_is_composited_before_rgb_conversion():
    """Respect palette transparency when converting to RGB."""
    input_image = Image.new("P", (1, 1), 0)
    input_image.putpalette([255, 0, 0] + [0, 0, 0] * 255)
    input_image.info["transparency"] = 0

    output_image = ModeProcessor(mode="RGB", background_color="#ffffff")(input_image)

    assert output_image.getpixel((0, 0)) == (255, 255, 255)


@pytest.mark.parametrize(
    ("input_pixel", "background_color", "expected"),
    [
        ((255, 255, 255, 0), "#000000", 0),
        ((0, 0, 0, 0), "#ffffff", 255),
        ((255, 255, 255, 128), "#000000", 255),
        ((255, 255, 255, 255), "#000000", 255),
    ],
)
def test_alpha_is_composited_before_binary_conversion(
    input_pixel: tuple[int, int, int, int], background_color: str, expected: int
):
    """Composite transparency over the configured background before thresholding.

    Arguments:
        input_pixel: RGBA input pixel
        background_color: configured compositing background
        expected: expected binary output pixel
    """
    input_image = Image.new("RGBA", (1, 1), input_pixel)

    output_image = ModeProcessor(mode="1", background_color=background_color)(
        input_image
    )

    assert output_image.getpixel((0, 0)) == expected


def test_alpha_is_preserved_when_target_mode_supports_it():
    """Preserve input alpha when converting to an alpha-capable output mode."""
    input_image = Image.new("LA", (1, 1), (200, 128))

    output_image = ModeProcessor(mode="LA", background_color="#ffffff")(input_image)

    assert output_image.getpixel((0, 0)) == (200, 128)
