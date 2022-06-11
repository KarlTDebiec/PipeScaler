#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for SizeSorter"""
import pytest

from pipescaler.pipelines.sorters import SizeSorter
from pipescaler.testing import get_infile, parametrized_fixture


@parametrized_fixture(
    cls=SizeSorter,
    params=[
        {"cutoff": 128},
    ],
)
def size_sorter(request) -> SizeSorter:
    return SizeSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("L", "greater_than_or_equal_to"),
    ],
)
def test(infile: str, outlet: str, size_sorter: SizeSorter) -> None:
    infile = get_infile(infile)

    assert size_sorter(infile) == outlet
