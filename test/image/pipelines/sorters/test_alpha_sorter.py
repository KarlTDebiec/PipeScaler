#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaSorter."""

from __future__ import annotations

import pytest

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import AlphaSorter
from pipescaler.testing.file import get_test_input_path


@pytest.fixture
def sorter() -> AlphaSorter:
    """Provide a fresh AlphaSorter instance for each test."""
    return AlphaSorter(threshold=255)


@pytest.mark.parametrize(
    ("input_filename", "outlet"),
    [
        ("L", "no_alpha"),
        ("extra/L_LA", "drop_alpha"),
        ("LA", "keep_alpha"),
        ("RGB", "no_alpha"),
        ("extra/RGB_RGBA", "drop_alpha"),
        ("RGBA", "keep_alpha"),
        ("PL", "no_alpha"),
        ("PLA", "keep_alpha"),
        ("PRGB", "no_alpha"),
        ("PRGBA", "keep_alpha"),
    ],
)
def test(input_filename: str, outlet: str, sorter: AlphaSorter):
    """Test AlphaSorter routing images based on alpha channel properties.

    Arguments:
        input_filename: Input image filename
        outlet: Expected outlet name for routing
        sorter: AlphaSorter fixture instance
    """
    img = PipeImage(path=get_test_input_path(input_filename))

    assert sorter(img) == outlet
