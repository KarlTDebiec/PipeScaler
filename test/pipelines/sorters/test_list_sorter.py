#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for ListSorter"""
import pytest

from pipescaler.core.pipelines.image import PipeImage
from pipescaler.pipelines.sorters import ListSorter
from pipescaler.testing import (
    get_test_infile_directory_path,
    get_test_infile_path,
    parametrized_fixture,
)


@parametrized_fixture(
    cls=ListSorter,
    params=[
        {
            "basic": get_test_infile_directory_path("basic"),
            "extra": get_test_infile_directory_path("extra"),
            "novel": get_test_infile_directory_path("novel"),
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
    image = PipeImage(path=get_test_infile_path(infile))
    assert sorter(image) == outlet
