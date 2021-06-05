#!/usr/bin/env python
#   pipescaler/processors/pngquant_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from os.path import isfile
from shutil import copyfile
from subprocess import Popen
from typing import Any

from pipescaler.core import Processor


####################################### CLASSES ########################################
class PngquantProcessor(Processor):

    # region Builtins

    def __init__(
        self,
        quality: int = 100,
        speed: int = 1,
        floyd_steinberg: bool = True,
        **kwargs: Any,
    ) -> None:
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

    def process_file_from_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(
            infile,
            outfile,
            self.pipeline.verbosity,
            quality=self.quality,
            speed=self.speed,
            floyd_steinberg=self.floyd_steinberg,
        )

    # endregion

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        parser.add_argument(
            "--quality",
            default="100",
            type=int,
            help="minimum quality below which output image will not be saved, "
            "and maximum quality above which fewer colors will be used, "
            "(1-100, default: %(default)s)",
        )
        parser.add_argument(
            "--speed",
            default=1,
            type=int,
            help="speed/quality balance (1-100, default: %(default)s)",
        )
        parser.add_argument(
            "--nofs",
            action="store_false",
            dest="floyd_steinberg",
            help="disable Floyd-Steinberg dithering",
        )

        return parser

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        quality = kwargs.get("quality", 100)
        speed = kwargs.get("speed", 1)
        floyd_steinberg = kwargs.get("floyd_steinberg", True)

        command = f"pngquant " f"--force " f"--quality {quality} " f"--speed {speed} "
        if not floyd_steinberg:
            command = f"{command} --nofs"
        command = f"{command} --output {outfile} {infile} "

        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # pngquant may not save outfile if it is too large or low quality
        if not isfile(outfile):
            copyfile(infile, outfile)


######################################### MAIN #########################################
if __name__ == "__main__":
    PngquantProcessor.main()
