#!python
# -*- coding: utf-8 -*-
#   lauhseuisin/processors/PngquantProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import expandvars, isfile
from shutil import copyfile
from subprocess import Popen
from typing import Any

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class PngquantProcessor(Processor):

    def __init__(self, quality: int = 100, speed: int = 1,
                 floyd_steinberg: bool = True, executable="pngquant",
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.quality = quality
        self.speed = speed
        self.floyd_steinberg = floyd_steinberg
        self.executable = expandvars(executable)
        self.desc = f"pngquant-{self.quality}-{self.speed}"
        if self.floyd_steinberg:
            self.desc = f"{self.desc}-fs"

    def process_file(self, infile: str, outfile: str) -> None:
        command = f"{self.executable} " \
                  f"--quality {self.quality} " \
                  f"--speed {self.speed} "
        if not self.floyd_steinberg:
            command = f"{command} --nofs"
        command = f"{command} --output {outfile} {infile} "

        if self.pipeline.verbosity >= 1:
            print(self.get_indented_text(command))
        Popen(command, shell=True, close_fds=True).wait()

        # pngquant may not save outfile if it is too large or low quality
        if not isfile(outfile):
            copyfile(infile, outfile)
