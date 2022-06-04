#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for SolidColorSorter"""
import pytest

from pipescaler.pipe.sorters import SolidColorSorter
from pipescaler.testing import get_infile, parametrized_fixture


@parametrized_fixture(
    cls=SolidColorSorter,
    params=[
        {"mean_threshold": 1, "max_threshold": 10},
    ],
)
def solid_color_sorter(request) -> SolidColorSorter:
    return SolidColorSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("L", "not_solid"),
        ("LA", "not_solid"),
        ("RGB", "not_solid"),
        ("RGBA", "not_solid"),
        ("PL", "not_solid"),
        ("PLA", "not_solid"),
        ("PRGB", "not_solid"),
        ("PRGBA", "not_solid"),
        ("novel/L_solid", "solid"),
        ("novel/LA_solid", "solid"),
        ("novel/RGB_solid", "solid"),
        ("novel/RGBA_solid", "solid"),
        ("novel/PL_solid", "solid"),
        ("novel/PLA_solid", "solid"),
        ("novel/PRGB_solid", "solid"),
        ("novel/PRGBA_solid", "solid"),
    ],
)
def test(infile: str, outlet: str, solid_color_sorter: SolidColorSorter) -> None:
    infile = get_infile(infile)

    assert solid_color_sorter(infile) == outlet
