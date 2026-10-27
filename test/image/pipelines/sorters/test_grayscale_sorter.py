#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for GrayscaleSorter."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import GrayscaleSorter
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=GrayscaleSorter,
    params=[
        {"mean_threshold": 1, "max_threshold": 10},
    ],
)
def sorter(request: pytest.FixtureRequest) -> GrayscaleSorter:
    """Pytest fixture that provides a GrayscaleSorter instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured GrayscaleSorter instance
    """
    return GrayscaleSorter(**request.param)


@pytest.mark.parametrize(
    ("input_filename", "outlet"),
    [
        ("L", "no_rgb"),
        ("LA", "no_rgb"),
        ("RGB", "keep_rgb"),
        ("RGBA", "keep_rgb"),
        ("PL", "no_rgb"),
        ("PLA", "no_rgb"),
        ("PRGB", "keep_rgb"),
        ("PRGBA", "keep_rgb"),
    ],
)
def test(input_filename: str, outlet: str, sorter: GrayscaleSorter):
    """Test GrayscaleSorter routing images based on grayscale properties.

    Arguments:
        input_filename: Input image filename
        outlet: Expected outlet name for routing
        sorter: GrayscaleSorter fixture instance
    """
    img = PipeImage(path=get_test_input_path(input_filename))

    assert sorter(img) == outlet


@pytest.mark.parametrize("color", [(100, 101, 100), (101, 100, 101)])
def test_small_channel_differences_route_to_drop_rgb(color: tuple[int, int, int]):
    """Test small RGB-to-grayscale differences in either signed direction.

    Arguments:
        color: RGB color with channel differences of one
    """
    sorter = GrayscaleSorter(mean_threshold=2, max_threshold=2)
    image = PipeImage(image=Image.new("RGB", (1, 1), color), name="small-difference")

    assert sorter(image) == "drop_rgb"
