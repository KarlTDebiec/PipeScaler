#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for in-memory libimagequant processing on every supported platform."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.validation import validate_image
from pipescaler.image.operators.processors import ImagequantProcessor
from pipescaler.testing.file import get_test_input_path


@pytest.mark.parametrize(
    "input_name", ["1", "L", "LA", "RGB", "RGBA", "PL", "PLA", "PRGB", "PRGBA"]
)
def test_supported_modes(input_name: str):
    """Quantize supported image modes without modifying input pixels or metadata.

    Arguments:
        input_name: existing input fixture name
    """
    with Image.open(get_test_input_path(input_name)) as image:
        original_pixels = image.tobytes()
        original_info = image.info.copy()

        output = ImagequantProcessor(min_quality=0)(image)

        assert output.mode == "P"
        assert output.size == image.size
        assert len(output.getcolors() or []) <= 256
        assert image.tobytes() == original_pixels
        assert image.info == original_info


@pytest.mark.parametrize("palette_mode", ["RGB", "RGBA"])
def test_palette_transparency_survives_repeated_quantization(palette_mode: str):
    """Keep visible colors and alpha in existing palettes and subsequent operators.

    Arguments:
        palette_mode: representation of the input palette's transparency
    """
    pixels = [(0, 0, 0, 0), (255, 0, 0, 128), (0, 255, 0, 255)]
    image = Image.frombytes("P", (3, 1), b"\x00\x01\x02")
    if palette_mode == "RGBA":
        image.putpalette([channel for pixel in pixels for channel in pixel], "RGBA")
    else:
        image.putpalette([channel for pixel in pixels for channel in pixel[:3]])
        image.info["transparency"] = bytes(pixel[3] for pixel in pixels)
    processor = ImagequantProcessor()

    output = processor(processor(image))

    assert output.mode == "P"
    rendered = np.array(validate_image(output).convert("RGBA"))
    assert rendered[0, :, 3].tolist() == [0, 128, 255]
    assert rendered[0, 1:].tolist() == [list(pixel) for pixel in pixels[1:]]


@pytest.mark.parametrize("dithering_level", [0.0, 1.0])
def test_palette_limit(dithering_level: float):
    """Reduce a many-color image to the configured palette size.

    Arguments:
        dithering_level: requested dithering strength
    """
    pixels = np.random.default_rng(168).integers(0, 256, (32, 32, 3), dtype=np.uint8)
    output = ImagequantProcessor(
        max_colors=8, min_quality=0, dithering_level=dithering_level
    )(Image.fromarray(pixels))

    assert output.mode == "P"
    assert 1 < len(output.getcolors() or []) <= 8


def test_quality_rejection_returns_original():
    """Return the original image when a tiny palette cannot meet perfect quality."""
    pixels = np.random.default_rng(168).integers(0, 256, (32, 32, 3), dtype=np.uint8)
    image = Image.fromarray(pixels)
    image.info["description"] = "original metadata"

    output = ImagequantProcessor(max_colors=2, min_quality=100)(image)

    assert output is image
    assert np.array_equal(np.array(output), pixels)
    assert output.info["description"] == "original metadata"


@pytest.mark.parametrize(
    "settings",
    [
        {"max_colors": 1},
        {"max_colors": 257},
        {"min_quality": -1},
        {"min_quality": 101},
        {"max_quality": -1},
        {"max_quality": 101},
        {"min_quality": 90, "max_quality": 80},
        {"dithering_level": -0.1},
        {"dithering_level": 1.1},
        {"dithering_level": float("nan")},
        {"dithering_level": float("inf")},
    ],
)
def test_invalid_settings(settings: dict[str, Any]):
    """Reject invalid settings before invoking native code.

    Arguments:
        settings: invalid quantizer settings
    """
    with pytest.raises(ValueError):
        ImagequantProcessor(**settings)


def test_other_native_errors_propagate(monkeypatch: pytest.MonkeyPatch):
    """Keep unexpected native failures distinct from minimum-quality rejection.

    Arguments:
        monkeypatch: pytest patch fixture
    """

    def fail(*args: Any, **kwargs: Any):
        """Simulate a native failure unrelated to quality.

        Arguments:
            *args: unused quantization arguments
            **kwargs: unused quantization settings
        Raises:
            RuntimeError: always
        """
        raise RuntimeError("Out of memory")

    monkeypatch.setattr("imagequant.quantize_raw_rgba_bytes", fail)

    with pytest.raises(RuntimeError, match="Out of memory"):
        ImagequantProcessor()(Image.new("RGB", (2, 2)))


def test_repr_round_trip():
    """Reconstruct non-default quantization settings from their representation."""
    processor = ImagequantProcessor(
        max_colors=16, min_quality=20, max_quality=80, dithering_level=0.5
    )

    assert repr(eval(repr(processor))) == repr(processor)


def test_unsupported_mode():
    """Reject unsupported modes before converting their pixel representation."""
    with pytest.raises(UnsupportedImageModeError):
        ImagequantProcessor()(Image.new("CMYK", (2, 2)))


def test_color_metadata_is_retained():
    """Retain color interpretation while replacing palette-specific transparency."""
    image = Image.new("RGB", (2, 2), (128, 128, 128))
    color_info = {
        "icc_profile": b"source RGB profile",
        "gamma": 1.0,
        "chromaticity": (0.3127, 0.329, 0.68, 0.32, 0.265, 0.69, 0.15, 0.06),
        "srgb": 0,
    }
    image.info.update(color_info)
    image.info["transparency"] = (128, 128, 128)

    output = ImagequantProcessor()(image)

    assert output.mode == "P"
    for key, value in color_info.items():
        assert output.info[key] == value
    assert output.convert("RGBA").getpixel((0, 0))[3] == 0


def test_sixteen_bit_grayscale_is_retained():
    """Retain 16-bit grayscale precision instead of clipping samples to 8 bits."""
    pixels = np.array([[0, 32768, 65535]], dtype=np.uint16)
    image = Image.fromarray(pixels)
    image.info["gamma"] = 1.0

    output = ImagequantProcessor()(image)

    assert output is image
    assert output.mode == "I;16"
    assert np.array_equal(np.array(output), pixels)
    assert output.info["gamma"] == 1.0


@pytest.mark.parametrize("mode", ["1", "L", "LA"])
def test_profiled_grayscale_is_retained(mode: str):
    """Avoid attaching a grayscale ICC profile to an RGB palette.

    Arguments:
        mode: grayscale input mode
    """
    image = Image.new(mode, (2, 2))
    image.info["icc_profile"] = b"source grayscale profile"

    assert ImagequantProcessor()(image) is image


@pytest.mark.parametrize("size", [(0, 1), (1, 0)])
def test_empty_image(size: tuple[int, int]):
    """Reject empty images before passing their buffers to native code.

    Arguments:
        size: image dimensions with an empty axis
    """
    with pytest.raises(ValueError, match="nonzero"):
        ImagequantProcessor()(Image.new("RGB", size))
