#!python
# -*- coding: utf-8 -*-
#   LauhSeuiSin.py
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

from lauhseuisin.processors import Processor


################################### CLASSES ###################################
class CopyProcessor(Processor):
    def __init__(self, output_directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.output_directory = expandvars(output_directory)

    def get_outfile(self, infile: str) -> str:
        return f"{self.output_directory}/{basename(dirname(infile))}.png"

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        copyfile(infile, outfile)

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        output_directories = kwargs.pop("output_directory")
        if not isinstance(output_directories, list):
            output_directories = [output_directories]

        processors: List[Processor] = []
        for output_directory in output_directories:
            processors.append(cls(
                output_directory=output_directory,
                **kwargs))
        return processors
