#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for image core functions."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.core.functions import is_monochrome


@pytest.mark.parametrize("pixel", [1, 254])
def test_is_monochrome_handles_differences_near_black_and_white(pixel: int):
    """Test small signed differences around the monochrome endpoints.

    Arguments:
        pixel: grayscale pixel value near black or white
    """
    image = Image.new("L", (1, 1), pixel)

    assert is_monochrome(image, mean_threshold=2, proportion_threshold=1)


def test_is_monochrome_rejects_differences_over_threshold():
    """Test a grayscale difference beyond the configured threshold."""
    image = Image.new("L", (1, 1), 250)

    assert not is_monochrome(image, mean_threshold=2, proportion_threshold=1)
