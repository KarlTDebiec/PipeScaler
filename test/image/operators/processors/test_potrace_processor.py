#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PotraceProcessor."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageOps

from pipescaler.image.operators.processors import PotraceProcessor
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=PotraceProcessor,
    params=[
        {},
        {"scale": 2},
    ],
)
def processor(request: pytest.FixtureRequest) -> PotraceProcessor:
    """Pytest fixture that provides a PotraceProcessor instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured PotraceProcessor instance
    """
    return PotraceProcessor(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        "1",
        "L",
        xfail_unsupported_image_mode()("LA"),
        xfail_unsupported_image_mode()("RGB"),
        xfail_unsupported_image_mode()("RGBA"),
        "PL",
        xfail_unsupported_image_mode()("PLA"),
        xfail_unsupported_image_mode()("PRGB"),
        xfail_unsupported_image_mode()("PRGBA"),
    ],
)
def test(input_filename: str, processor: PotraceProcessor):
    """Test PotraceProcessor with various image modes.

    Arguments:
        input_filename: Input image filename
        processor: PotraceProcessor fixture instance
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.mode == "L"
    assert output_img.size == (
        input_img.size[0] * processor.scale,
        input_img.size[1] * processor.scale,
    )


@pytest.mark.parametrize("width", [1, 31, 32, 33, 63, 64, 65])
def test_orientation_and_word_boundaries(width: int):
    """Preserve asymmetric shapes across native bitmap word boundaries.

    Arguments:
        width: input width near 32-bit and 64-bit word boundaries
    """
    image = Image.new("L", (width, 17), 255)
    ImageDraw.Draw(image).rectangle((0, 0, width - 1, 4), fill=0)
    output = PotraceProcessor(turdsize=0, alphamax=0)(image)
    assert output.getpixel((width - 1, 1)) < 128
    assert output.getpixel((width - 1, 15)) == 255


def test_nested_holes():
    """Retain white holes and black islands in a compound trace."""
    image = Image.new("L", (40, 40), 255)
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 2, 37, 37), fill=0)
    draw.rectangle((10, 10, 29, 29), fill=255)
    draw.rectangle((16, 16, 23, 23), fill=0)
    output = PotraceProcessor(alphamax=0)(image)
    assert [output.getpixel((x, x)) for x in (0, 5, 12, 20)] == [255, 0, 255, 0]


@pytest.mark.parametrize("value", [0, 255])
@pytest.mark.parametrize("invert", [False, True])
def test_solid_images(value: int, invert: bool):
    """Handle empty and full traces with either inversion setting.

    Arguments:
        value: uniform grayscale input value
        invert: whether to invert before and after tracing
    """
    output = PotraceProcessor(invert=invert, alphamax=0)(Image.new("L", (12, 9), value))
    assert output.mode == "L"
    assert output.getextrema() == (value, value)


def test_inversion_equivalence():
    """Invert before thresholding and restore output polarity afterward."""
    image = Image.new("L", (20, 20), 30)
    ImageDraw.Draw(image).ellipse((5, 2, 18, 15), fill=210)
    actual = PotraceProcessor(invert=True, scale=1.5)(image)
    expected = ImageOps.invert(PotraceProcessor(scale=1.5)(ImageOps.invert(image)))
    np.testing.assert_array_equal(np.asarray(actual), np.asarray(expected))


def test_threshold_and_speckle_controls():
    """Apply the grayscale cutoff and native speckle suppression."""
    image = Image.new("L", (20, 20), 255)
    ImageDraw.Draw(image).rectangle((2, 2, 8, 8), fill=100)
    image.putpixel((15, 15), 0)
    low = PotraceProcessor(blacklevel=0.3, turdsize=2, alphamax=0)(image)
    high = PotraceProcessor(blacklevel=0.5, turdsize=0, alphamax=0)(image)
    assert low.getextrema() == (255, 255)
    assert high.getpixel((4, 4)) == 0
    assert high.getpixel((15, 15)) < 255


@pytest.mark.parametrize("scale", [0.5, 1.25, 2.0])
def test_fractional_scaling(scale: float):
    """Truncate scaled dimensions while retaining grayscale antialiasing.

    Arguments:
        scale: output scale relative to input dimensions
    """
    image = Image.new("L", (19, 23), 255)
    ImageDraw.Draw(image).ellipse((2, 2, 15, 18), fill=0)
    output = PotraceProcessor(scale=scale)(image)
    assert output.size == (int(19 * scale), int(23 * scale))
    assert output.mode == "L"
    pixels = np.asarray(output)
    assert np.any((pixels > 0) & (pixels < 255))


@pytest.mark.parametrize(
    "settings",
    [
        {"scale": 0},
        {"scale": -1},
        {"scale": float("inf")},
        {"scale": float("nan")},
        {"blacklevel": -0.1},
        {"blacklevel": 1.1},
        {"alphamax": -1},
        {"opttolerance": -1},
        {"turdsize": -1},
        {"turnpolicy": "unknown"},
    ],
)
def test_invalid_settings(settings: dict[str, Any]):
    """Reject invalid typed tracing settings before native execution.

    Arguments:
        settings: invalid constructor arguments
    """
    with pytest.raises(ValueError):
        PotraceProcessor(**settings)


def test_too_small_output():
    """Reject a positive scale that would truncate a dimension to zero."""
    with pytest.raises(ValueError, match="at least one pixel"):
        PotraceProcessor(scale=0.01)(Image.new("L", (10, 10)))


def test_repr():
    """Reconstruct every setting without loading a library."""
    processor = PotraceProcessor(
        blacklevel=0.4,
        turdsize=5,
        turnpolicy="left",
        alphamax=0.8,
        opticurve=False,
        opttolerance=0.5,
        invert=True,
        scale=1.25,
    )
    assert repr(eval(repr(processor))) == repr(processor)


def test_no_file_exchange(monkeypatch: pytest.MonkeyPatch):
    """Process an image without saving any intermediate bitmap or raster.

    Arguments:
        monkeypatch: fixture for preventing Pillow file writes
    """

    def fail_save(*args: Any, **kwargs: Any):
        """Reject any attempted image file exchange.

        Arguments:
            *args: ignored save arguments
            **kwargs: ignored save options
        Raises:
            AssertionError: if the processor attempts to save a file
        """
        raise AssertionError("Tracing must stay in memory")

    monkeypatch.setattr(Image.Image, "save", fail_save)
    assert PotraceProcessor()(Image.new("L", (10, 10))).mode == "L"
