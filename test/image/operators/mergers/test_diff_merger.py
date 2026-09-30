#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for DiffMerger."""

from __future__ import annotations

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


def test_rejects_mismatched_modes():
    """Test that input images must have matching modes."""
    merger = DiffMerger()

    first = Image.new("L", (4, 4), 0)
    second = Image.new("RGB", (4, 4), (255, 255, 255))

    with pytest.raises(ValueError, match="modes must match"):
        merger(first, second)


def test_rejects_mismatched_aspect_ratio():
    """Test that input images must have matching aspect ratios."""
    merger = DiffMerger()

    first = Image.new("RGB", (4, 2), (0, 0, 0))
    second = Image.new("RGB", (4, 3), (255, 255, 255))

    with pytest.raises(ValueError, match="aspect ratios must match"):
        merger(first, second)
