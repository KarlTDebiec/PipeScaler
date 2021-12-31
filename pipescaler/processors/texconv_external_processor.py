#!/usr/bin/env python
#   pipescaler/processors/texconv_external_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Compresses image using Texconv"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import debug, info
from os.path import basename, join
from shutil import copyfile
from tempfile import TemporaryDirectory
from typing import Any, Optional

from pipescaler.common import run_command, validate_executable
from pipescaler.core import Processor


class TexconvExternalProcessor(Processor):
    """
    Compresses image using
    [Texconv](https://github.com/Microsoft/DirectXTex/wiki/Texconv)
    """

    extension = "dds"

    def __init__(
        self,
        mipmaps: bool = False,
        sepalpha: bool = False,
        filetype: Optional[str] = "DDS",
        format: Optional[str] = "BC7_UNORM",
        **kwargs: Any,
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            mipmaps: Whether or not to generate mipmaps
            sepalpha: Whether or not to generate mips alpha channel separately from
              color channels
            filetype: Output file type
            format: Output format
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.mipmaps = mipmaps
        self.sepalpha = sepalpha
        self.filetype = filetype
        self.format = format

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = validate_executable("texconv.exe", {"Windows"})

        with TemporaryDirectory() as temp_directory:
            # Stage image
            tempfile = join(temp_directory, basename(infile))
            copyfile(infile, tempfile)

            # Process image
            if self.mipmaps:
                if self.sepalpha:
                    command += f" -sepalpha"
            else:
                command += f" -m 1"
            if self.filetype:
                command += f" -ft {self.filetype}"
            if self.format:
                command += f" -f {self.format}"
            command += f" -o {temp_directory} {tempfile}"
            debug(f"{self}: {command}")
            run_command(command)

            # Write image
            copyfile(f"{tempfile[:-4]}.dds", outfile)  # TODO: Handle filetypes
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
            "--mipmaps",
            action="store_true",
            help="generate mipmaps",
        )
        parser.add_argument(
            "--sepalpha",
            action="store_true",
            help="generate mips alpha channel separately from color channels",
        )
        parser.add_argument(
            "--filetype",
            type=str,
            help="output file type",
        )
        parser.add_argument(
            "--format",
            default="BC7_UNORM",
            type=str,
            help="output format",
        )

        return parser


if __name__ == "__main__":
    TexconvExternalProcessor.main()
