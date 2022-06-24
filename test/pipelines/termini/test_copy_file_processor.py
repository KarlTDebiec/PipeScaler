#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for CopyFileTerminus"""
from tempfile import TemporaryDirectory

from pipescaler.core.pipelines import PipeImage
from pipescaler.pipelines.termini import CopyFileTerminus
from pipescaler.testing import get_sub_directory


def test() -> None:
    with TemporaryDirectory() as output_directory:
        terminus = CopyFileTerminus(directory=output_directory)

        for infile in get_sub_directory("basic").iterdir():
            terminus(PipeImage(path=infile))
        for infile in get_sub_directory("basic").iterdir():
            terminus(PipeImage(path=infile))
        for infile in get_sub_directory("alt").iterdir():
            terminus(PipeImage(path=infile))

        terminus = CopyFileTerminus(directory=output_directory)
        terminus.purge_unrecognized_files()
