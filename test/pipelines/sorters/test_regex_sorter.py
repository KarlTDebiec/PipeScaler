#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for RegexSorter."""
from __future__ import annotations

import pytest

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.pipelines.sorters import RegexSorter
from pipescaler.testing.file import get_test_infile_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=RegexSorter,
    params=[
        dict(
            regex=".*L.*",
        ),
    ],
)
def sorter(request) -> RegexSorter:
    return RegexSorter(**request.param)


@pytest.mark.parametrize(
    ("infile_name", "outlet"),
    [
        ("1", "unmatched"),
        ("L", "matched"),
        ("LA", "matched"),
        ("RGB", "unmatched"),
        ("RGBA", "unmatched"),
    ],
)
def test(infile_name: str, outlet: str, sorter: RegexSorter) -> None:
    image = PipeImage(path=get_test_infile_path(infile_name))
    assert sorter(image) == outlet

    # Test miscellaneous methods
    print(sorter)
    print(repr(sorter))
    print(sorter.outlets)
    print(sorter.help_markdown())
