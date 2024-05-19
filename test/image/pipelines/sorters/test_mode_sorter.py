#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ModeSorter."""
import pytest

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.sorters import ModeSorter
from pipescaler.testing.file import get_test_infile_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=ModeSorter,
    params=[
        {},
    ],
)
def sorter(request) -> ModeSorter:
    return ModeSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("1", "M"),
        ("L", "L"),
        ("LA", "LA"),
        ("RGB", "RGB"),
        ("RGBA", "RGBA"),
        ("PL", "L"),
        ("PLA", "LA"),
        ("PRGB", "RGB"),
        ("PRGBA", "RGBA"),
    ],
)
def test(infile: str, outlet: str, sorter: ModeSorter) -> None:
    image = PipeImage(path=get_test_infile_path(infile))

    assert sorter(image) == outlet
