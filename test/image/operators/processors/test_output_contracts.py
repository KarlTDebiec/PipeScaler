#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression coverage for declared image output and validation contracts."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.core.validation import (
    validate_image,
    validate_image_and_convert_mode,
)
from pipescaler.image.operators.processors import PotraceProcessor, ThresholdProcessor
from pipescaler.testing.file import get_test_input_path


@pytest.mark.parametrize("mode", ["1", "L", "P"])
@pytest.mark.parametrize("denoise", [False, True])
def test_threshold_output_contract(mode: str, denoise: bool):
    """Return mode 1 for every accepted input while preserving threshold decisions.

    Arguments:
        mode: input image mode, including a grayscale palette
        denoise: whether to denoise the thresholded pixels
    """
    image = Image.new("L", (4, 1))
    image.putdata([0, 128, 129, 255])
    if mode == "1":
        image = image.convert("1", dither=Image.Dither.NONE)
    elif mode == "P":
        image = image.convert("P")
    processor = ThresholdProcessor(denoise=denoise)

    output = processor(image)

    assert processor.outputs() == {"output": ("1",)}
    assert output.mode in processor.outputs()["output"]
    assert output.size == image.size
    if mode == "1":
        assert output.mode == "1"
        assert output.tobytes() == image.tobytes()
    else:
        assert output.mode == "1"
        assert np.asarray(output.convert("L")).flatten().tolist() == [0, 0, 255, 255]


@pytest.mark.parametrize("mode", ["1", "L", "P"])
@pytest.mark.parametrize("background", [0, 255])
@pytest.mark.parametrize("denoise", [False, True])
def test_threshold_isolated_pixel(mode: str, background: int, denoise: bool):
    """Preserve binary output and denoise isolated black or white pixels.

    Arguments:
        mode: input image mode
        background: surrounding pixel value
        denoise: whether the isolated pixel is removed
    """
    image = Image.new("L", (3, 3), background)
    image.putpixel((1, 1), 255 - background)
    image = image.convert(mode, dither=Image.Dither.NONE)

    output = ThresholdProcessor(denoise=denoise)(image)

    assert output.mode == "1"
    expected = [background] * 9
    if not denoise:
        expected[4] = 255 - background
    assert np.asarray(output.convert("L")).flatten().tolist() == expected


@pytest.mark.parametrize("mode", ["1", "L", "P"])
@pytest.mark.parametrize("invert", [False, True])
def test_potrace_output_contract(mode: str, invert: bool):
    """Keep grayscale output for every accepted input mode and inversion setting.

    Arguments:
        mode: input image mode, including a grayscale palette
        invert: whether input and output inversion are enabled
    """
    image = Image.new("L", (16, 16), 255)
    for y in range(4, 12):
        for x in range(4, 12):
            image.putpixel((x, y), 0)
    image = image.convert(mode, dither=Image.Dither.NONE)
    processor = PotraceProcessor(invert=invert, scale=2)

    output = processor(image)

    assert processor.outputs() == {"output": ("L",)}
    assert output.mode == "L"
    assert output.size == (32, 32)
    pixels = np.asarray(output)
    assert pixels[16, 16] == 0
    assert pixels[0, 16] == 255
    assert np.any((pixels > 0) & (pixels < 255))


def test_unsupported_mode_diagnostic():
    """Identify rejected modes and the supported alternatives in the error."""
    with pytest.raises(UnsupportedImageModeError) as exc_info:
        validate_image(Image.new("RGB", (1, 1)), ("L", "1"))

    assert str(exc_info.value) == (
        "Mode 'RGB' is not among supported modes: ['1', 'L']"
    )


def test_validation_reports_mode_after_palette_removal():
    """Return the expanded palette mode before an optional conversion."""
    image = Image.new("L", (1, 1), 128).convert("P")

    output, original_mode = validate_image_and_convert_mode(image, "L", "RGB")

    assert original_mode == "L"
    assert output.mode == "RGB"
    assert output.getpixel((0, 0)) == (128, 128, 128)


@pytest.mark.parametrize("processor_type", [PotraceProcessor, ThresholdProcessor])
@pytest.mark.parametrize(
    "input_filename", ["LA", "RGB", "RGBA", "PLA", "PRGB", "PRGBA"]
)
def test_grayscale_processors_reject_color_or_alpha(
    processor_type: type[PotraceProcessor] | type[ThresholdProcessor],
    input_filename: str,
):
    """Reject unsupported modes after expanding palettes.

    Arguments:
        processor_type: grayscale-only processor
        input_filename: unsupported color or alpha fixture
    """
    with Image.open(get_test_input_path(input_filename)) as image:
        with pytest.raises(
            UnsupportedImageModeError, match="is not among supported modes"
        ):
            processor_type()(image)
