#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for HistogramMatchMerger."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.operators.mergers import HistogramMatchMerger
from pipescaler.image.testing import get_expected_output_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=HistogramMatchMerger,
    params=[
        {},
    ],
)
def merger(request: pytest.FixtureRequest) -> HistogramMatchMerger:
    """Pytest fixture that provides a HistogramMatchMerger instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured HistogramMatchMerger instance
    """
    return HistogramMatchMerger(**request.param)


@pytest.mark.parametrize(
    ("ref", "fit"),
    [
        ("alt/L", "L"),
        ("alt/LA", "LA"),
        ("alt/RGB", "RGB"),
        ("alt/RGBA", "RGBA"),
        ("alt/PL", "PL"),
        ("alt/PLA", "PLA"),
        ("alt/PRGB", "PRGB"),
        ("alt/PRGBA", "PRGBA"),
    ],
)
def test(ref: str, fit: str, merger: HistogramMatchMerger):
    """Test HistogramMatchMerger with reference and fit images.

    Arguments:
        ref: Reference image filename
        fit: Image to fit to reference filename
        merger: HistogramMatchMerger fixture instance
    """
    ref_input_path = get_test_input_path(ref)
    ref_img = Image.open(ref_input_path)
    fit_input_path = get_test_input_path(fit)
    fit_img = Image.open(fit_input_path)

    output_img = merger(ref_img, fit_img)

    assert output_img.mode == get_expected_output_mode(fit_img)
    assert output_img.size == fit_img.size


@pytest.mark.parametrize(
    ("mode", "reference_pixel", "fit_pixel"),
    [
        ("L", 200, 20),
        ("LA", (200, 128), (20, 255)),
        ("RGB", (255, 0, 0), (0, 0, 255)),
        ("RGBA", (255, 0, 0, 64), (0, 0, 255, 192)),
    ],
)
def test_matches_pixel_channels(
    mode: str,
    reference_pixel: int
    | tuple[int, int]
    | tuple[int, int, int]
    | tuple[int, int, int, int],
    fit_pixel: int | tuple[int, int] | tuple[int, int, int] | tuple[int, int, int, int],
    merger: HistogramMatchMerger,
):
    """Match pixel channel values for grayscale and color images.

    Arguments:
        mode: Pillow image mode
        reference_pixel: pixel value in the reference image
        fit_pixel: pixel value in the image to fit
        merger: histogram merger instance
    """
    reference = Image.new(mode, (3, 2), reference_pixel)
    fit = Image.new(mode, (2, 3), fit_pixel)

    output = merger(reference, fit)

    assert output.mode == mode
    assert output.size == fit.size
    assert output.getpixel((0, 0)) == reference_pixel


def test_matches_palette_converted_images(merger: HistogramMatchMerger):
    """Match palette images after conversion to their underlying color modes.

    Arguments:
        merger: histogram merger instance
    """
    reference = Image.new("P", (3, 2), 0)
    reference.putpalette([255, 0, 0, 0, 0, 255] + [0] * (768 - 6))
    fit = Image.new("P", (2, 3), 1)
    fit.putpalette([255, 0, 0, 0, 0, 255] + [0] * (768 - 6))

    output = merger(reference, fit)

    assert output.mode == "RGB"
    assert output.size == fit.size
    assert output.getpixel((0, 0)) == (255, 0, 0)
