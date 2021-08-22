#!/usr/bin/env python
#   test_termini.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
""""""
from os.path import join
from tempfile import TemporaryDirectory

from pipescaler.termini import CopyFileTerminus
from shared import alt_infiles, infiles


def test_copy_file_terminus() -> None:
    with TemporaryDirectory() as output_directory:
        terminus = CopyFileTerminus(directory=output_directory)

        for infile, infile_path in infiles.items():
            terminus(infile_path, join(terminus.directory, infile))
        for infile, infile_path in infiles.items():
            terminus(infile_path, join(terminus.directory, infile))
        for infile, infile_path in alt_infiles.items():
            terminus(infile_path, join(terminus.directory, infile))

        terminus = CopyFileTerminus(directory=output_directory, purge=True)

        for infile, infile_path in infiles.items():
            terminus(infile_path, join(terminus.directory, infile))
