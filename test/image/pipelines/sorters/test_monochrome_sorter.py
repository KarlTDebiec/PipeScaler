#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for MonochromeSorter"""
import pytest

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import MonochromeSorter
from pipescaler.testing import get_test_infile_path, parametrized_fixture


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
    image = PipeImage(path=get_test_infile_path(infile))

    assert sorter(image) == outlet
