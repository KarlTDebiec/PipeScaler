#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for GrayscaleSorter"""
import pytest

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import GrayscaleSorter
from pipescaler.testing.file import get_test_infile_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=GrayscaleSorter,
    params=[
        {"mean_threshold": 1, "max_threshold": 10},
    ],
)
def sorter(request) -> GrayscaleSorter:
    return GrayscaleSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
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
def test(infile: str, outlet: str, sorter: GrayscaleSorter) -> None:
    image = PipeImage(path=get_test_infile_path(infile))

    assert sorter(image) == outlet
