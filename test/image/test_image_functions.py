#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for image functions."""

from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.image.core.functions import expand_image


def test_expand_image_places_asymmetric_padding_at_requested_offsets():
    """Test expansion keeps the source at the requested left and top offsets."""
    image = Image.fromarray(np.array([[10, 20, 30, 40]], dtype=np.uint8))

    expanded = expand_image(image, left=2, right=0)

    np.testing.assert_array_equal(
        np.array(expanded), np.array([[20, 10, 10, 20, 30, 40]], dtype=np.uint8)
    )


def test_expand_image_repeats_reflections_for_large_padding():
    """Test large padding reflects repeatedly without leaving blank pixels."""
    image = Image.fromarray(np.array([[1, 2], [3, 4]], dtype=np.uint8))

    expanded = expand_image(image, left=8, top=8, right=1, bottom=1)

    expected = np.array(
        [
            [1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2],
            [3, 4, 4, 3, 3, 4, 4, 3, 3, 4, 4],
            [3, 4, 4, 3, 3, 4, 4, 3, 3, 4, 4],
            [1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2],
            [1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2],
            [3, 4, 4, 3, 3, 4, 4, 3, 3, 4, 4],
            [3, 4, 4, 3, 3, 4, 4, 3, 3, 4, 4],
            [1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2],
            [1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2],
            [3, 4, 4, 3, 3, 4, 4, 3, 3, 4, 4],
            [3, 4, 4, 3, 3, 4, 4, 3, 3, 4, 4],
        ],
        dtype=np.uint8,
    )
    np.testing.assert_array_equal(np.array(expanded), expected)


def test_expand_image_handles_odd_and_singleton_dimensions():
    """Test odd dimensions and a singleton axis retain reflected source pixels."""
    image = Image.fromarray(np.array([[5], [8], [13]], dtype=np.uint8))

    expanded = expand_image(image, left=1, top=2, right=2, bottom=1)

    np.testing.assert_array_equal(
        np.array(expanded),
        np.array(
            [
                [8, 8, 8, 8],
                [5, 5, 5, 5],
                [5, 5, 5, 5],
                [8, 8, 8, 8],
                [13, 13, 13, 13],
                [13, 13, 13, 13],
            ],
            dtype=np.uint8,
        ),
    )
