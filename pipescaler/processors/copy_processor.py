#!/usr/bin/env python
#   pipescaler/processors/copy_processor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from shutil import copyfile
from typing import Any

from pipescaler.common import validate_output_path
from pipescaler.processors.processor import Processor


####################################### CLASSES ########################################
class CopyFileProcessor(Processor):

    # region Builtins

    def __init__(self, output_directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.output_directory = output_directory

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return "copyfile"
        return self._desc

    @property
    def output_directory(self) -> str:
        """str: Output path"""
        if not hasattr(self, "_output_directory"):
            raise ValueError()
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value: str) -> None:
        self._output_directory = validate_output_path(
            value, file_ok=False, directory_ok=True
        )

    # endregion

    # region Methods

    def get_outfile(self, infile: str) -> str:
        original_name = self.get_original_name(infile)
        extension = self.get_original_name(infile)
        return f"{self.output_directory}/{original_name}.{extension}"

    # endregion

    # region Class Methods

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs
    ) -> None:
        if verbosity >= 1:
            print(f"Copying {infile} to {outfile}")
        copyfile(infile, outfile)

    # endregion
