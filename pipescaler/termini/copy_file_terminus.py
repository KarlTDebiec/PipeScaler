#!/usr/bin/env python
#   pipescaler/termini/copy_file_terminus.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from logging import info
from os import remove
from shutil import copyfile
from typing import Any

from pipescaler.common import validate_output_path
from pipescaler.core import Terminus, parse_file_list


####################################### CLASSES ########################################
class CopyFileTerminus(Terminus):

    # region Builtins

    def __init__(
        self, output_directory: str, purge: bool = False, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.directory = validate_output_path(
            output_directory, file_ok=False, directory_ok=True
        )

        if purge:
            for filename in parse_file_list(self.directory, True):
                remove(filename)
                info(f"{self}: '{filename}' removed")

    # endregion

    # region Class Methods

    @classmethod
    def process_file(cls, infile: str, outfile: str, **kwargs) -> None:
        copyfile(infile, outfile)
        info(f"{cls}: '{outfile}' saved")

    # endregion
