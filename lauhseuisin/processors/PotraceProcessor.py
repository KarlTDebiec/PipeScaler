#!python
# -*- coding: utf-8 -*-
#   lauhseuisin/processors/PotraceProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os import remove
from os.path import expandvars, splitext
from subprocess import Popen
from typing import Any

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class PotraceProcessor(Processor):

    def __init__(self, blacklevel: float = 0.3, alphamax: float = 1.34,
                 opttolerance: float = 0.2,
                 convert_executable: str = "convert",
                 potrace_executable: str = "potrace", **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.blacklevel = blacklevel
        self.alphamax = alphamax
        self.opttolerance = opttolerance
        self.convert_executable = expandvars(convert_executable)
        self.potrace_executable = expandvars(potrace_executable)
        self.desc = f"potrace-{self.blacklevel:4.2f}-" \
                    f"{self.alphamax:4.2f}-{self.opttolerance:3.1f}"

    def process_file(self, infile: str, outfile: str) -> None:
        # Convert to bmp; potrace does not accept png
        bmpfile = f"{splitext(infile)[0]}.bmp"
        command = f"{self.convert_executable} " \
                  f"{infile} " \
                  f"{bmpfile}"
        if self.pipeline.verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # trace
        svgfile = f"{splitext(outfile)[0]}.svg"
        command = f"{self.potrace_executable} " \
                  f"{bmpfile} " \
                  f"-b svg " \
                  f"-k {self.blacklevel} " \
                  f"-a {self.alphamax} " \
                  f"-O {self.opttolerance} " \
                  f"-o {svgfile}"
        if self.pipeline.verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # Rasterize svg to png
        command = f"{self.convert_executable} " \
                  f"{svgfile} " \
                  f"{outfile}"
        if self.pipeline.verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # Clean up
        remove(bmpfile)
        remove(svgfile)
