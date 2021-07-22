#!/usr/bin/env python
#   pipescaler/processors/side_channel_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from logging import info
from os.path import basename, dirname, splitext
from shutil import copyfile
from typing import Any

from pipescaler.common import validate_input_path
from pipescaler.core import Processor, parse_file_list


####################################### CLASSES ########################################
class SideChannelProcessor(Processor):

    # region Builtins

    def __init__(self, directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.directory = validate_input_path(
            directory, file_ok=False, directory_ok=True
        )
        self.side_files = {}
        for filename in parse_file_list(self.directory, full_paths=True):
            filename_base = splitext(basename(filename))[0]
            self.side_files[filename_base] = filename

    def __call__(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, side_files=self.side_files)

    @classmethod
    def process_file(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        side_files = kwargs.get("side_files", {})
        infile_base = basename(dirname(infile))
        if infile_base in side_files:
            copyfile(side_files[infile_base], outfile)
            info(f"{cls}: '{outfile}' saved")
        else:
            raise FileNotFoundError()
