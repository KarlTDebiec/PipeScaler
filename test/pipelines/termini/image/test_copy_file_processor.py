#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for CopyImageTerminus."""
from tempfile import TemporaryDirectory

from pipescaler.core.pipelines.image import PipeImage
from pipescaler.pipelines.termini.image import CopyImageTerminus
from pipescaler.testing import get_test_infile_directory_path


def test() -> None:
    with TemporaryDirectory() as output_directory:
        terminus = CopyImageTerminus(directory=output_directory)

        for infile in get_test_infile_directory_path("basic").iterdir():
            terminus(PipeImage(path=infile))
        for infile in get_test_infile_directory_path("basic").iterdir():
            terminus(PipeImage(path=infile))
        for infile in get_test_infile_directory_path("alt").iterdir():
            terminus(PipeImage(path=infile))

        terminus = CopyImageTerminus(directory=output_directory)
        terminus.purge_unrecognized_files()
