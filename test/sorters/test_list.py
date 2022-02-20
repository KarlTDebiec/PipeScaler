#!/usr/bin/env python
#   test/sorters/test_list.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for ListSorter"""

import pytest

from pipescaler.sorters import ListSorter
from pipescaler.testing import get_sub_directory, stage_fixture


@stage_fixture(
    cls=ListSorter,
    params=[
        {
            "outlets": {
                "basic": get_sub_directory("basic"),
                "extra": get_sub_directory("extra"),
                "novel": get_sub_directory("novel"),
            }
        },
    ],
)
def list_sorter(request) -> ListSorter:
    return ListSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("L", "basic"),
        ("1_L", "extra"),
        ("L_solid", "novel"),
    ],
)
def test(infile: str, outlet: str, list_sorter: ListSorter) -> None:
    pass
