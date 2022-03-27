#!/usr/bin/env python
#   test/sorters/test_mode_sorter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for ModeSorter"""
import pytest

from pipescaler.sorters import ModeSorter
from pipescaler.testing import get_infile, stage_fixture


@stage_fixture(
    cls=ModeSorter,
    params=[
        {},
    ],
)
def mode_sorter(request) -> ModeSorter:
    return ModeSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("1", "1"),
        ("L", "l"),
        ("LA", "la"),
        ("RGB", "rgb"),
        ("RGBA", "rgba"),
        ("PL", "l"),
        ("PLA", "la"),
        ("PRGB", "rgb"),
        ("PRGBA", "rgba"),
    ],
)
def test(infile: str, outlet: str, mode_sorter: ModeSorter) -> None:
    infile = get_infile(infile)

    assert mode_sorter(infile) == outlet
