#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for GrayscaleSorter"""
import pytest

from pipescaler.core.pipelines.image import PipeImage
from pipescaler.pipelines.sorters.image import GrayscaleSorter
from pipescaler.testing import get_test_infile_path, parametrized_fixture


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
