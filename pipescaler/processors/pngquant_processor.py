#!/usr/bin/env python
#   pipescaler/processors/pngquant_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from logging import debug, info
from os.path import isfile
from shutil import copyfile
from subprocess import PIPE, Popen
from typing import Any

from pipescaler.common import validate_executable, validate_int
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
        """
        Validates and stores static configuration.

        Arguments:
        quality (int): minimum quality below which output image will not be saved, and
          maximum quality above which fewer colors will be used
        speed (int): speed/quality balance
        floyd_steinberg (bool): disable Floyd-Steinberg dithering
        """
        super().__init__(**kwargs)

        # Store configuration
        self.quality = validate_int(quality, 1, 100)
        self.speed = validate_int(speed, 1, 100)
        self.floyd_steinberg = floyd_steinberg

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Processes infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        validate_executable("pngquant")
        super().__call__(infile, outfile)

    # endregion

    # region Methods

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Loads image, processes it using pngquant, and saves resulting output

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Process image
        command = f"pngquant --skip-if-larger --force"
        command += f" --quality {self.quality}"
        command += f" --speed {self.speed}"
        if not self.floyd_steinberg:
            command += f" --nofs"
        command += f" --output {outfile} {infile} "
        debug(f"{self}: {command}")
        child = Popen(command, shell=True, close_fds=True, stdout=PIPE, stderr=PIPE)
        exitcode = child.wait(10)
        if exitcode == 98:
            # pngquant may not save outfile if it is too large or low quality
            copyfile(infile, outfile)
        elif exitcode != 0:
            raise ValueError()  # TODO: Provide useful output

        # Write image
        info(f"{self}: '{outfile}' saved")

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

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    PngquantProcessor.main()
