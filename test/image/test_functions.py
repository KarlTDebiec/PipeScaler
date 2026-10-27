#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for image functions."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.core.functions import smooth_image


@pytest.mark.parametrize(
    ("value", "sigma"),
    [
        (value, sigma)
        for value in (1, 17, 100, 128, 254, 255)
        for sigma in (0.5, 1.0, 2.0, 3.5)
    ],
)
def test_smooth_image_preserves_constant_image(value: int, sigma: float):
    """Smoothing preserves a constant image's height values.

    Arguments:
        value: constant height value
        sigma: gaussian standard deviation
    """
    image = Image.new("L", (11, 9), value)

    smoothed = smooth_image(image, sigma)

    assert smoothed.mode == "L"
    assert np.array_equal(np.array(smoothed), np.full((9, 11), value, dtype=np.uint8))


@pytest.mark.parametrize(
    ("sigma", "expected_pixels"),
    [
        (0.5, (158, 21, 0)),
        (1.0, (41, 25, 5)),
        (2.0, (10, 9, 6)),
    ],
)
def test_smooth_image_blurs_impulse_with_expected_strength(
    sigma: float, expected_pixels: tuple[int, int, int]
):
    """Smoothing spreads an isolated height peak according to sigma.

    Arguments:
        sigma: gaussian standard deviation
        expected_pixels: expected center and neighboring pixel values
    """
    values = np.zeros((41, 41), dtype=np.uint8)
    values[20, 20] = 255
    image = Image.fromarray(values)

    smoothed = np.array(smooth_image(image, sigma))

    assert tuple(smoothed[20, 20:23]) == expected_pixels
    assert smoothed[20, 20] < 255


def test_smooth_image_zero_sigma_returns_unchanged_pixels():
    """Zero sigma leaves pixel values unchanged."""
    image = Image.fromarray(np.array([[0, 127, 255]], dtype=np.uint8))

    smoothed = smooth_image(image, 0)

    assert smoothed is not image
    assert np.array_equal(np.array(smoothed), np.array(image))


@pytest.mark.parametrize("sigma", [-1.0, float("inf"), float("nan")])
def test_smooth_image_rejects_invalid_sigma(sigma: float):
    """Smoothing rejects negative and non-finite sigma values.

    Arguments:
        sigma: invalid gaussian standard deviation
    """
    image = Image.new("L", (3, 3), 100)

    with pytest.raises(ValueError, match="sigma"):
        smooth_image(image, sigma)
