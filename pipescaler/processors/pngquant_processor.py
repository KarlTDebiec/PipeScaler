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
from logging import info
from os.path import isfile
from shutil import copyfile, which
from subprocess import Popen
from typing import Any

from pipescaler.common import ExecutableNotFoundError, validate_int
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

        # Store configuration
        self.quality = validate_int(quality, 1, 100)
        self.speed = validate_int(speed, 1, 100)
        self.floyd_steinberg = floyd_steinberg

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Scales infile by self.scale and writes the resulting image to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        if not which("pngquant"):
            raise ExecutableNotFoundError("pngquant executable not found in PATH")
        self.process_file(
            infile,
            outfile,
            quality=self.quality,
            speed=self.speed,
            floyd_steinberg=self.floyd_steinberg,
        )

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        parser.add_argument(
            "--quality",
            default="100",
            type=cls.int_arg(1, 100),
            help="minimum quality below which output image will not be saved, "
            "and maximum quality above which fewer colors will be used, "
            "(1-100, default: %(default)s)",
        )
        parser.add_argument(
            "--speed",
            default=1,
            type=cls.int_arg(1, 100),
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
    def process_file(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        quality = kwargs.get("quality", 100)
        speed = kwargs.get("speed", 1)
        floyd_steinberg = kwargs.get("floyd_steinberg", True)

        # Scale image
        command = f"pngquant --skip-if-larger --force"
        command += f" --quality {quality}"
        command += f" --speed {speed}"
        if not floyd_steinberg:
            command += f" --nofs"
        command += f" --output {outfile} {infile} "
        Popen(command, shell=True, close_fds=True).wait()
        # pngquant may not save outfile if it is too large or low quality
        if not isfile(outfile):
            copyfile(infile, outfile)
        info(f"{cls}: '{outfile}' saved")

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    PngquantProcessor.main()
