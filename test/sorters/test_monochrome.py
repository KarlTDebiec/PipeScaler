#!/usr/bin/env python
#   test/sorters/test_monochrome.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for MonochromeSorter"""
import pytest

from pipescaler.sorters import MonochromeSorter
from pipescaler.testing import get_infile, stage_fixture


@stage_fixture(
    cls=MonochromeSorter,
    params=[
        {"mean_threshold": 1, "max_threshold": 10},
    ],
)
def monochrome_sorter(request) -> MonochromeSorter:
    return MonochromeSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("1", "no_gray"),
        ("extra/1_L", "drop_gray"),
        ("L", "keep_gray"),
    ],
)
def test(infile: str, outlet: str, monochrome_sorter: MonochromeSorter) -> None:
    infile = get_infile(infile)

    assert monochrome_sorter(infile) == outlet
