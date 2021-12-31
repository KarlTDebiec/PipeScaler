#!/usr/bin/env python
#   pipescaler/processors/pngquant_external_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Compresses image palette using pngquant"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import debug, info
from shutil import copyfile
from typing import Any

from pipescaler.common import run_command, validate_executable, validate_int
from pipescaler.core import Processor


class PngquantExternalProcessor(Processor):
    """Compresses image palette using [pngquant](https://pngquant.org/)"""

    def __init__(
        self,
        quality: int = 100,
        speed: int = 1,
        floyd_steinberg: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            quality: Minimum quality below which output image will not be saved, and
              maximum quality above which fewer colors will be used
            speed: Speed/quality balance
            floyd_steinberg: Disable Floyd-Steinberg dithering
        """
        super().__init__(**kwargs)

        # Store configuration
        self.quality = validate_int(quality, 1, 100)
        self.speed = validate_int(speed, 1, 100)
        self.floyd_steinberg = floyd_steinberg

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = validate_executable("pngquant")

        # Process image
        command += (
            f" --skip-if-larger"
            f" --force"
            f" --quality {self.quality}"
            f" --speed {self.speed}"
            f" --output {outfile} "
        )
        if not self.floyd_steinberg:
            command += f" --nofs"
        command += f" {infile} "
        debug(f"{self}: {command}")
        exitcode, stdout, stderr = run_command(command, acceptable_exitcodes=[0, 98])
        if exitcode == 98:
            # pngquant may not save outfile if it is too large or low quality
            copyfile(infile, outfile)

        # Write image
        info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Args:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop("description", cleandoc(cls.__doc__))
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


if __name__ == "__main__":
    PngquantExternalProcessor.main()
