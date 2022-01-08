#!/usr/bin/env python
#   test_sources.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
import pytest
from shared import infile_subfolders, xfail_value

from pipescaler.sources import CitraSource, DirectorySource, DolphinSource, TexmodSource


@pytest.mark.parametrize(
    ("directory"),
    [
        (infile_subfolders["basic"]),
        ([infile_subfolders["basic"], infile_subfolders["extra"]]),
    ],
)
def test_directory_source(directory: str) -> None:
    source = DirectorySource(directory)
    for infile in source:
        pass


@pytest.mark.parametrize(
    ("directory"),
    [
        xfail_value()(infile_subfolders["basic"]),
        xfail_value()([infile_subfolders["basic"], infile_subfolders["extra"]]),
    ],
)
def test_citra_source(directory: str) -> None:
    source = CitraSource(directory)
    for infile in source:
        pass


@pytest.mark.parametrize(
    ("directory"),
    [
        xfail_value()(infile_subfolders["basic"]),
        xfail_value()([infile_subfolders["basic"], infile_subfolders["extra"]]),
    ],
)
def test_dolphin_source(directory: str) -> None:
    source = DolphinSource(directory)
    for infile in source:
        pass


@pytest.mark.parametrize(
    ("directory"),
    [
        xfail_value()(infile_subfolders["basic"]),
        xfail_value()([infile_subfolders["basic"], infile_subfolders["extra"]]),
    ],
)
def test_texmod_source(directory: str) -> None:
    source = TexmodSource(directory)
    for infile in source:
        pass
