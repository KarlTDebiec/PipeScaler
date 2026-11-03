#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for shared image validation contracts."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.core.validation import validate_image_scale


@pytest.mark.parametrize(
    ("reference_size", "target_size", "min_scale", "expected"),
    [
        ((2, 3), (2, 3), 1, 1),
        ((2, 3), (4, 6), 1, 2),
        ((2, 3), (4, 6), 2, 2),
        ((2, 3), (6, 9), 3, 3),
        ((3, 2), (9, 6), 2, 3),
    ],
)
def test_validate_image_scale_returns_shared_integer(
    reference_size: tuple[int, int],
    target_size: tuple[int, int],
    min_scale: int,
    expected: int,
):
    """Return the uniform dimension scale independently of image mode or content.

    Arguments:
        reference_size: reference width and height
        target_size: target width and height
        min_scale: minimum accepted scale
        expected: resulting scale
    """
    reference = Image.new("L", reference_size, 17)
    target = Image.new("RGB", target_size, (1, 2, 3))

    actual = validate_image_scale(reference, target, min_scale=min_scale)

    assert actual == expected
    assert isinstance(actual, int)


@pytest.mark.parametrize(
    ("reference_size", "target_size", "min_scale"),
    [
        ((2, 3), (2, 3), 2),
        ((2, 3), (4, 6), 3),
        ((4, 6), (2, 3), 1),
        ((2, 3), (4, 9), 1),
        ((2, 3), (4, 7), 1),
        ((2, 3), (5, 6), 1),
        ((2, 3), (4, 3), 1),
        ((0, 3), (4, 6), 1),
        ((2, 0), (4, 6), 1),
        ((2, 3), (0, 6), 1),
        ((2, 3), (4, 0), 1),
        ((0, 0), (0, 0), 1),
    ],
)
def test_validate_image_scale_rejects_unsupported_dimensions(
    reference_size: tuple[int, int], target_size: tuple[int, int], min_scale: int
):
    """Reject empty, fractional, nonuniform, or insufficient scales.

    Arguments:
        reference_size: reference width and height
        target_size: target width and height
        min_scale: minimum accepted scale
    """
    reference = Image.new("L", reference_size)
    target = Image.new("L", target_size)

    with pytest.raises(ValueError, match="uniform integer scale") as raised:
        validate_image_scale(reference, target, min_scale=min_scale)

    assert f"reference {reference_size}" in str(raised.value)
    assert f"target {target_size}" in str(raised.value)


@pytest.mark.parametrize("min_scale", [0, -1])
def test_validate_image_scale_rejects_nonpositive_minimum(min_scale: int):
    """Reject a minimum that permits zero or negative scales.

    Arguments:
        min_scale: unsupported minimum scale
    """
    image = Image.new("L", (2, 3))

    with pytest.raises(ValueError, match="min_scale must be at least 1"):
        validate_image_scale(image, image, min_scale=min_scale)
