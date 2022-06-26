#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for MonochromeSorter"""
import pytest

from pipescaler.core.pipelines import PipeImage
from pipescaler.pipelines.sorters import MonochromeSorter
from pipescaler.testing import get_infile, parametrized_fixture


@parametrized_fixture(
    cls=MonochromeSorter,
    params=[
        {"mean_threshold": 1, "max_threshold": 10},
    ],
)
def sorter(request) -> MonochromeSorter:
    return MonochromeSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("1", "no_gray"),
        ("extra/1_L", "drop_gray"),
        ("L", "keep_gray"),
    ],
)
def test(infile: str, outlet: str, sorter: MonochromeSorter) -> None:
    image = PipeImage(path=get_infile(infile))

    assert sorter(image) == outlet
