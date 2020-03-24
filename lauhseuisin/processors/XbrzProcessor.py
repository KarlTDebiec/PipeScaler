#!python
# -*- coding: utf-8 -*-
#   lauhseuisin/processors/XbrzProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import expandvars
from subprocess import Popen
from typing import Any

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class XbrzProcessor(Processor):

    def __init__(self, scale: int = 4, executable="xbrzscale",
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.scale = scale
        self.executable = expandvars(executable)
        self.desc = f"xbrz-{self.scale}"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.executable, self.scale,
                          self.pipeline.verbosity)

    @classmethod
    def process_file(cls, infile: str, outfile: str, executable: str,
                     scale: int, verbosity: int) -> None:
        command = f"{executable} " \
                  f"{scale} " \
                  f"{infile} " \
                  f"{outfile}"
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()
