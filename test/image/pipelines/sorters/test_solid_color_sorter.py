#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SolidColorSorter"""

import pytest

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import SolidColorSorter
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=SolidColorSorter,
    params=[
        {"mean_threshold": 1, "max_threshold": 10},
    ],
)
def sorter(request) -> SolidColorSorter:
    return SolidColorSorter(**request.param)


@pytest.mark.parametrize(
    ("input_filename", "outlet"),
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
def test(input_filename: str, outlet: str, sorter: SolidColorSorter) -> None:
    img = PipeImage(path=get_test_input_path(input_filename))

    assert sorter(img) == outlet
