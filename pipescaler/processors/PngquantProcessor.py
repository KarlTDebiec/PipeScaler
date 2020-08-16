#!/usr/bin/env python
#   pipescaler/processors/PngquantProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import isfile
from shutil import copyfile
from subprocess import Popen
from typing import Any

from pipescaler.processors.Processor import Processor


################################### CLASSES ###################################
class PngquantProcessor(Processor):

    # region Builtins

    def __init__(self, quality: int = 100, speed: int = 1,
                 floyd_steinberg: bool = True, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.quality = quality
        self.speed = speed
        self.floyd_steinberg = floyd_steinberg

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            if self.floyd_steinberg:
                return f"pngquant-{self.quality}-{self.speed}-fs"
            else:
                return f"pngquant-{self.quality}-{self.speed}"
        return self._desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.pipeline.verbosity,
                          quality=self.quality, speed=self.speed,
                          floyd_steinberg=self.floyd_steinberg)

    # endregion

    @classmethod
    def process_file(cls, infile: str, outfile: str, verbosity: int = 1,
                     **kwargs: Any) -> None:
        quality = kwargs.get("quality")
        speed = kwargs.get("speed")
        floyd_steinberg = kwargs.get("floyd_steinberg")

        command = f"pngquant " \
                  f"--quality {quality} " \
                  f"--speed {speed} "
        if not floyd_steinberg:
            command = f"{command} --nofs"
        command = f"{command} --output {outfile} {infile} "

        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # pngquant may not save outfile if it is too large or low quality
        if not isfile(outfile):
            copyfile(infile, outfile)
