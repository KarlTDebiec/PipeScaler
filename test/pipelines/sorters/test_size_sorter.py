#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for SizeSorter"""
import pytest

from pipescaler.core.pipelines import PipeImage
from pipescaler.pipelines.sorters.image import SizeSorter
from pipescaler.testing import get_test_infile_path, parametrized_fixture


@parametrized_fixture(
    cls=SizeSorter,
    params=[
        {"cutoff": 128},
    ],
)
def sorter(request) -> SizeSorter:
    return SizeSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("L", "greater_than_or_equal_to"),
    ],
)
def test(infile: str, outlet: str, sorter: SizeSorter) -> None:
    image = PipeImage(path=get_test_infile_path(infile))

    assert sorter(image) == outlet
