#!python
#   lauhseuisin/processors/CopyFileProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import basename, dirname, expandvars, isfile
from shutil import copyfile
from typing import Any, List

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class CopyFileProcessor(Processor):
    def __init__(self, output_directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.output_directory = expandvars(output_directory)
        self.desc = self.output_directory

    def get_outfile(self, infile: str) -> str:
        original_name = basename(dirname(infile))
        return f"{self.output_directory}/{original_name}.png"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.pipeline.verbosity)

    @classmethod
    def process_file(cls, infile: str, outfile: str, verbosity: int) -> None:
        if isfile(outfile):
            return
        if verbosity >= 1:
            print(cls.get_indented_text(f"cp {infile} {outfile}"))
        copyfile(infile, outfile)
