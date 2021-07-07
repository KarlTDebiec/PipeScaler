#!/usr/bin/env python
#   pipescaler/processors/texconv_processor.py
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
from os.path import basename, join
from platform import win32_ver
from shutil import copyfile, which
from subprocess import Popen
from tempfile import TemporaryDirectory
from typing import Any, Optional

from pipescaler.common import ExecutableNotFoundError
from pipescaler.core import Processor, UnsupportedPlatformError


####################################### CLASSES ########################################
class TexconvProcessor(Processor):
    extension = "dds"

    # region Builtins

    def __init__(
        self,
        sepalpha: bool = False,
        filetype: Optional[str] = None,
        format: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.sepalpha = sepalpha
        self.filetype = filetype
        self.format = format

    def __call__(self, infile: str, outfile: str) -> None:
        if not any(win32_ver()):
            raise UnsupportedPlatformError(
                "TexconvProcessor is only supported on Windows"
            )
        if not which("texconv.exe"):
            raise ExecutableNotFoundError("texconv.exe executable not found in PATH")
        self.process_file(
            infile,
            outfile,
            sepalpha=self.sepalpha,
            filetype=self.filetype,
            format=self.format,
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
            "--sepalpha",
            action="store_true",
            help="resize/generate mips alpha channel separately from color channels",
        )
        parser.add_argument(
            "--filetype", type=str, help="output file type",
        )
        parser.add_argument(
            "--format", type=str, help="output format",
        )

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        sepalpha = kwargs.get("sepalpha", False)
        filetype = kwargs.get("filetype")
        format = kwargs.get("format")

        with TemporaryDirectory() as temp_directory:
            # Stage image
            tempfile = join(temp_directory, basename(infile))
            copyfile(infile, tempfile)

            # Convert image
            command = f"texconv.exe"
            if sepalpha:
                command = f"{command} -sepalpha"
            if filetype:
                command = f"{command} -ft {filetype}"
            if format:
                command = f"{command} -f {format}"
            command = f"{command} -o {temp_directory} {tempfile}"
            debug(f"{cls}: {command}")
            Popen(command, shell=True, close_fds=True).wait()

            # Write image
            copyfile(f"{tempfile[:-4]}.dds", outfile)
            info(f"{cls}: '{outfile}' saved")


######################################### MAIN #########################################
if __name__ == "__main__":
    TexconvProcessor.main()
