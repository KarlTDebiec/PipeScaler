#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for Sources"""
from pytest import mark

from pipescaler.core.pipe import Source
from pipescaler.pipe.sources import DirectorySource
from pipescaler.testing import get_sub_directory


@mark.parametrize(
    ("source"),
    [
        (DirectorySource(get_sub_directory("basic"))),
    ],
)
def test(source: Source) -> None:
    for image in source:
        assert image.parents is None
