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

    def process_file(self, infile: str, outfile: str) -> None:
        command = f"{self.executable} " \
                  f"{self.scale} " \
                  f"{infile} " \
                  f"{outfile}"
        if self.pipeline.verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()
