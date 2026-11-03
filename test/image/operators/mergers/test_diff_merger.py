#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for DiffMerger."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.operators.mergers import DiffMerger


def test_blue_black_red_gradient_direction():
    """Test that signed differences map to blue-black-red colors."""
    merger = DiffMerger()

    first = Image.new("L", (3, 1))
    first.putdata([128, 128, 128])
    second = Image.new("L", (3, 1))
    second.putdata([0, 128, 255])

    output = merger(first, second)

    assert output.mode == "RGB"
    assert output.getpixel((0, 0))[2] > 0
    assert output.getpixel((0, 0))[0] == 0
    assert output.getpixel((1, 0)) == (0, 0, 0)
    assert output.getpixel((2, 0))[0] > 0
    assert output.getpixel((2, 0))[2] == 0


def test_equal_brightness_color_change_is_red():
    """Keep chromatic changes visible when their channel averages match."""
    result = DiffMerger()(
        Image.new("RGB", (1, 1), "red"), Image.new("RGB", (1, 1), "lime")
    )
    red, green, blue = result.getpixel((0, 0))
    assert red > 0
    assert green == blue == 0


def test_identical_nearest_neighbor_upscale_is_black():
    """Treat an unchanged nearest-neighbor enlargement as identical."""
    first = Image.frombytes("RGB", (2, 1), bytes([10, 20, 30, 200, 100, 50]))
    second = first.resize((6, 3), Image.Resampling.NEAREST)
    output = DiffMerger()(first, second)
    assert output.size == second.size
    assert output.getbbox() is None


def test_rejects_empty_image():
    """Reject zero-sized images before aspect-ratio arithmetic."""
    with pytest.raises(ValueError, match="dimensions must be positive"):
        DiffMerger()(Image.new("L", (0, 1)), Image.new("L", (1, 1)))


def test_rejects_mismatched_aspect_ratio():
    """Test that input images must have matching aspect ratios."""
    merger = DiffMerger()

    first = Image.new("RGB", (4, 2), (0, 0, 0))
    second = Image.new("RGB", (4, 3), (255, 255, 255))

    with pytest.raises(ValueError, match="aspect ratios must match"):
        merger(first, second)


def test_rejects_mismatched_modes():
    """Test that input images must have matching modes."""
    merger = DiffMerger()

    first = Image.new("L", (4, 4), 0)
    second = Image.new("RGB", (4, 4), (255, 255, 255))

    with pytest.raises(ValueError, match="modes must match"):
        merger(first, second)


@pytest.mark.parametrize("count", [0, 1, 3])
def test_rejects_wrong_input_count(count: int):
    """Reject missing or extra images before reading pixel data.

    Arguments:
        count: supplied image count
    """
    with pytest.raises(ValueError, match="Expected 2 input images"):
        DiffMerger()(*[Image.new("RGB", (1, 1)) for _ in range(count)])


def test_resizes_smaller_input_with_nearest_neighbor():
    """Test that smaller image is resized to match larger image."""
    merger = DiffMerger()

    first = Image.new("L", (4, 4), 128)
    second = Image.new("L", (2, 2), 255)

    output = merger(first, second)

    assert output.size == (4, 4)
    for x in range(4):
        for y in range(4):
            red, _, blue = output.getpixel((x, y))
            assert red > 0
            assert blue == 0


def test_weighted_rgb_magnitudes_match_independent_calculation():
    """Preserve weighted distance and direction across compiled pixel processing."""
    rng = np.random.default_rng(824)
    first = rng.integers(0, 256, (3, 5, 3), dtype=np.uint8)
    second = rng.integers(0, 256, (3, 5, 3), dtype=np.uint8)
    first[0, 0] = second[0, 0]
    expected = np.zeros_like(first)
    maximum = (2 + 127.5 / 256 + 4 + 2 + (255 - 127.5) / 256) * 255**2
    for y in range(3):
        for x in range(5):
            a = first[y, x].astype(float)
            b = second[y, x].astype(float)
            delta = b - a
            mean_red = (a[0] + b[0]) / 2
            squared = (
                (2 + mean_red / 256) * delta[0] ** 2
                + 4 * delta[1] ** 2
                + (2 + (255 - mean_red) / 256) * delta[2] ** 2
            )
            magnitude = round(255 * (squared / maximum) ** 0.5)
            if delta.mean() >= 0:
                channel = 0
            else:
                channel = 2
            expected[y, x, channel] = magnitude
    output = DiffMerger()(Image.fromarray(first), Image.fromarray(second))
    np.testing.assert_array_equal(np.asarray(output), expected)
