#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaSorter"""
import pytest

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import AlphaSorter
from pipescaler.testing.file import get_test_infile_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=AlphaSorter,
    params=[
        {"threshold": 255},
    ],
)
def sorter(request) -> AlphaSorter:
    return AlphaSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("L", "no_alpha"),
        ("extra/L_LA", "drop_alpha"),
        ("LA", "keep_alpha"),
        ("RGB", "no_alpha"),
        ("extra/RGB_RGBA", "drop_alpha"),
        ("RGBA", "keep_alpha"),
        ("PL", "no_alpha"),
        ("PLA", "keep_alpha"),
        ("PRGB", "no_alpha"),
        ("PRGBA", "keep_alpha"),
    ],
)
def test(infile: str, outlet: str, sorter: AlphaSorter) -> None:
    image = PipeImage(path=get_test_infile_path(infile))

    assert sorter(image) == outlet
