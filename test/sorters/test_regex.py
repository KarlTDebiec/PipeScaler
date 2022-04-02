#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for RegexSorter"""
import pytest

from pipescaler.sorters import RegexSorter
from pipescaler.testing import parametrized_fixture


@parametrized_fixture(
    cls=RegexSorter,
    params=[
        {"regex": ".*L.*"},
    ],
)
def regex_sorter(request) -> RegexSorter:
    return RegexSorter(**request.param)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        ("1", "unmatched"),
        ("L", "matched"),
        ("LA", "matched"),
        ("RGB", "unmatched"),
        ("RGBA", "unmatched"),
    ],
)
def test(infile: str, outlet: str, regex_sorter: RegexSorter) -> None:
    pass
