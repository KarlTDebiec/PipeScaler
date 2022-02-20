#!/usr/bin/env python
#   test/sources/test_directory.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for DirectorySource"""
from pipescaler.sources import DirectorySource
from pipescaler.testing import get_sub_directory, stage_fixture


@stage_fixture(
    cls=DirectorySource,
    params=[
        {"directory": get_sub_directory("basic")},
        {"directory": [get_sub_directory("basic"), get_sub_directory("extra")]},
    ],
)
def directory_source(request) -> DirectorySource:
    return DirectorySource(**request.param)


def test(directory_source: DirectorySource) -> None:
    for infile in directory_source:
        pass
