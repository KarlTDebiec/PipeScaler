#!/usr/bin/env python
#   pipescaler/processors/copy_file_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from shutil import copyfile
from typing import Any

from pipescaler.common import validate_output_path
from pipescaler.core import Processor


####################################### CLASSES ########################################
class CopyFileProcessor(Processor):

    # region Builtins

    def __init__(self, output_directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.output_directory = validate_output_path(
            output_directory, file_ok=False, directory_ok=True
        )

    # endregion

    # region Properties

    @property
    def outlets(self):
        return []

    # endregion

    # region Class Methods

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs
    ) -> None:
        if verbosity >= 1:
            print(f"Copying image from '{infile}' to '{outfile}'")
        copyfile(infile, outfile)

    # endregion
