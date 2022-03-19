#!/usr/bin/env python
#   pipescaler/processors/external/pngquant_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Compresses image palette using pngquant"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import debug
from shutil import copyfile
from typing import Any

from pipescaler.common import run_command, validate_executable, validate_int
from pipescaler.core import ExternalProcessor


class PngquantProcessor(ExternalProcessor):
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
        self.quality = quality
        self.speed = validate_int(speed, 1, 100)
        self.floyd_steinberg = floyd_steinberg

    @property
    def command_template(self):
        """String template with which to generate command"""
        command = (
            f"{validate_executable(self.executable, self.supported_platforms)}"
            " --skip-if-larger"
            " --force"
            f" --quality {self.quality}"
            f" --speed {self.speed}"
        )
        if not self.floyd_steinberg:
            command += " --nofs"
        command += " --output {outfile} {infile}"

        return command

    @property
    def executable(self) -> str:
        """Name of executable"""
        return "pngquant"

    def process(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = self.command_template.format(infile=infile, outfile=outfile)
        debug(f"{self}: {command}")
        exitcode, stdout, stderr = run_command(
            command, acceptable_exitcodes=[0, 98, 99]
        )
        if exitcode in [98, 99]:
            # pngquant may not save outfile if it is too large or low quality
            copyfile(infile, outfile)

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
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
    PngquantProcessor.main()
