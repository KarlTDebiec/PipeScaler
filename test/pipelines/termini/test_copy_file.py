#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for CopyFileTerminus"""
from os.path import basename, join
from tempfile import TemporaryDirectory

from pytest import fixture

from pipescaler.core import get_files
from pipescaler.pipelines.termini import CopyFileTerminus
from pipescaler.testing import get_sub_directory


@fixture()
def infiles() -> set[str]:
    return get_files(get_sub_directory("basic"), style="absolute")


@fixture()
def alt_infiles() -> set[str]:
    return get_files(get_sub_directory("alt"), style="absolute")


def test(infiles: set[str], alt_infiles: set[str]) -> None:
    with TemporaryDirectory() as output_directory:
        terminus = CopyFileTerminus(directory=output_directory)

        for infile in infiles:
            terminus(infile, join(terminus.directory, basename(infile)))
        for infile in infiles:
            terminus(infile, join(terminus.directory, basename(infile)))
        for infile in alt_infiles:
            terminus(infile, join(terminus.directory, basename(infile)))

        terminus = CopyFileTerminus(directory=output_directory, purge=True)

        for infile in alt_infiles:
            terminus(infile, join(terminus.directory, basename(infile)))
