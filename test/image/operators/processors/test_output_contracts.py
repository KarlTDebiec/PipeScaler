#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression coverage for declared image output and validation contracts."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.core.validation import (
    validate_image,
    validate_image_and_convert_mode,
)
from pipescaler.image.operators.processors import PotraceProcessor, ThresholdProcessor


@pytest.mark.parametrize("mode", ["1", "L", "P"])
@pytest.mark.parametrize("denoise", [False, True])
def test_threshold_output_contract(mode: str, denoise: bool):
    """Declare both binary and grayscale output without changing threshold pixels.

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

    assert processor.outputs() == {"output": ("1", "L")}
    assert output.mode in processor.outputs()["output"]
    if mode == "1":
        assert output.mode == "1"
        assert output.tobytes() == image.tobytes()
    else:
        assert output.mode == "L"
        assert np.asarray(output).flatten().tolist() == [0, 0, 255, 255]


@pytest.mark.parametrize("mode", ["1", "L", "P"])
@pytest.mark.parametrize("invert", [False, True])
def test_potrace_output_contract(
    monkeypatch: pytest.MonkeyPatch, mode: str, invert: bool
):
    """Keep grayscale raster values and advertise mode L for every accepted input.

    Arguments:
        monkeypatch: fixture for replacing external tracing and rasterization
        mode: input image mode, including a grayscale palette
        invert: whether tracing and output inversion are enabled
    """
    processor = PotraceProcessor(invert=invert, scale=2)
    monkeypatch.setattr(processor.potrace_runner, "run", Mock())
    monkeypatch.setattr(
        "pipescaler.image.operators.processors.potrace_processor.svg2rlg",
        Mock(return_value=Mock(width=2, height=1)),
    )

    def rasterize(drawing: object, output_path: Path, fmt: str):
        """Stand in for the renderer with black, gray, and white RGB pixels.

        Arguments:
            drawing: scaled drawing supplied by the processor
            output_path: temporary raster destination
            fmt: renderer output format
        """
        assert fmt == "png"
        raster = Image.new("L", (4, 2))
        raster.putdata([0, 64, 192, 255] * 2)
        raster.convert("RGB").save(output_path)

    monkeypatch.setattr(
        "pipescaler.image.operators.processors.potrace_processor.drawToFile", rasterize
    )
    image = Image.new(mode, (2, 1))
    if mode == "P":
        image.putpalette([value for value in range(256) for _ in range(3)])

    output = processor(image)

    assert processor.outputs() == {"output": ("L",)}
    assert output.mode in processor.outputs()["output"]
    assert output.size == (4, 2)
    expected = [0, 64, 192, 255] * 2
    if invert:
        expected = [255 - value for value in expected]
    assert np.asarray(output).flatten().tolist() == expected


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
