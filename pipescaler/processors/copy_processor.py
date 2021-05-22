#!/usr/bin/env python
#   pipescaler/processors/copy_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import isfile
from shutil import copyfile
from typing import Any

from pipescaler.common import get_ext, validate_input_path, validate_output_path
from pipescaler.core import PipeImage, Processor


####################################### CLASSES ########################################
class CopyFileProcessor(Processor):

    # region Builtins

    def __init__(self, output_directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.output_directory = output_directory

        # Prepare description
        desc = f"{self.name} {self.__class__.__name__} ({self.output_directory})"
        if self.downstream_stages is not None:
            if len(self.downstream_stages) >= 2:
                for stage in self.downstream_stages[:-1]:
                    desc += f"\n ├─ {stage}"
            desc += f"\n └─ {self.downstream_stages[-1]}"
        self.desc = desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, image: PipeImage) -> None:
        infile = validate_input_path(image.last)
        outfile = validate_output_path(
            f"{self.output_directory}/{image.name}.{get_ext(image.last)}"
        )
        if not isfile(outfile):
            self.process_file(infile, outfile, verbosity=self.pipeline.verbosity)
        image.log(self.name, outfile)

    # endregion

    # region Properties

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
