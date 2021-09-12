#!/usr/bin/env python
#   pipescaler/processors/texconv_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from argparse import ArgumentParser
from logging import debug, info
from os.path import basename, join
from platform import win32_ver
from shutil import copyfile
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory
from typing import Any, Optional

from pipescaler.common import validate_executable
from pipescaler.core import Processor, UnsupportedPlatformError


class TexconvProcessor(Processor):
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
        Validates and stores static configuration.

        Arguments:
        mipmaps (bool): whether or not to generate mipmaps
        sepalpha (bool): whether or not to generate mips alpha channel separately from
          color channels
        filetype (Optional[str]): output file type
        format (Optional[str]): output format
        kwargs (Any): Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.mipmaps = mipmaps
        self.sepalpha = sepalpha
        self.filetype = filetype
        self.format = format

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Processes infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """
        if not any(win32_ver()):
            raise UnsupportedPlatformError(
                "TexconvProcessor is only supported on Windows"
            )
        validate_executable("texconv.exe")
        super().__call__(infile, outfile)

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Loads image, converts it using texconv, and saves resulting output.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        with TemporaryDirectory() as temp_directory:
            # Stage image
            tempfile = join(temp_directory, basename(infile))
            copyfile(infile, tempfile)

            # Process image
            command = "texconv.exe"
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
            child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
            exitcode = child.wait(10)
            if exitcode != 0:
                raise ValueError()  # TODO: Provide useful output

            # Write image
            copyfile(f"{tempfile[:-4]}.dds", outfile)  # TODO: Handle filetypes
            info(f"{self}: '{outfile}' saved")

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
            "--mipmaps", action="store_true", help="generate mipmaps",
        )
        parser.add_argument(
            "--sepalpha",
            action="store_true",
            help="generate mips alpha channel separately from color channels",
        )
        parser.add_argument(
            "--filetype", type=str, help="output file type",
        )
        parser.add_argument(
            "--format", default="BC7_UNORM", type=str, help="output format",
        )

        return parser


if __name__ == "__main__":
    TexconvProcessor.main()
