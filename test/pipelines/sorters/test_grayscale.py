#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for GrayscaleSorter"""
import pytest

from pipescaler.pipelines.sorters import GrayscaleSorter
from pipescaler.testing import get_infile, parametrized_fixture


@parametrized_fixture(
    cls=GrayscaleSorter,
    params=[
        {"mean_threshold": 1, "max_threshold": 10},
    ],
)
def grayscale_sorter(request) -> GrayscaleSorter:
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
def test(infile: str, outlet: str, grayscale_sorter: GrayscaleSorter) -> None:
    infile = get_infile(infile)

    assert grayscale_sorter(infile) == outlet
