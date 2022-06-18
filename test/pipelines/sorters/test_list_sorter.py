#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for ListSorter"""
import pytest

from pipescaler.core.pipelines import PipeImage
from pipescaler.pipelines.sorters import ListSorter
from pipescaler.testing import get_infile, get_sub_directory, parametrized_fixture


@parametrized_fixture(
    cls=ListSorter,
    params=[
        {
            "basic": get_sub_directory("basic"),
            "extra": get_sub_directory("extra"),
            "novel": get_sub_directory("novel"),
        },
    ],
)
def sorter(request) -> ListSorter:
    return ListSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("basic/L", "basic"),
        ("extra/1_L", "extra"),
        ("novel/L_solid", "novel"),
    ],
)
def test(infile: str, outlet: str, sorter: ListSorter) -> None:
    image = PipeImage(path=get_infile(infile))
    assert sorter(image) == outlet
