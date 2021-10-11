#!/usr/bin/env python
#   pipescaler/termini/copy_file_terminus.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from hashlib import md5
from logging import info
from os import remove
from os.path import isfile
from shutil import copyfile
from typing import Any

from pipescaler.common import validate_output_path
from pipescaler.core import Terminus, get_files


class CopyFileTerminus(Terminus):
    """Copies images to a defined output directory."""

    def __init__(self, directory: str, purge: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.directory = validate_output_path(
            directory, file_ok=False, directory_ok=True, create_directory=True
        )

        if purge:
            for filename in get_files(self.directory, style="absolute"):
                remove(filename)
                info(f"{self}: '{filename}' removed")

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            infile_md5sum = md5(open(infile, "rb").read()).hexdigest()
            outfile_md5sum = md5(open(outfile, "rb").read()).hexdigest()
            if infile_md5sum == outfile_md5sum:
                info(f"{self}: '{outfile}' unchanged; not overwritten")
            else:
                copyfile(infile, outfile)
                info(f"{self}: '{outfile}' changed; overwritten")
        else:
            copyfile(infile, outfile)
            info(f"{self}: '{outfile}' saved")
