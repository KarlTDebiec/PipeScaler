#!/usr/bin/env python
#   pipescaler/processors/texconv_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from os.path import basename, isfile, join
from platform import win32_ver
from shutil import copyfile, which
from subprocess import Popen
from tempfile import TemporaryDirectory
from typing import Any, Optional

from pipescaler.common import ExecutableNotFoundError, validate_output_path
from pipescaler.core import PipeImage, UnsupportedPlatformError, Processor


####################################### CLASSES ########################################
class TexconvProcessor(Processor):

    # region Builtins

    def __init__(
        self,
        sepalpha: bool = False,
        filetype: Optional[str] = None,
        format: Optional[str] = None,
        **kwargs: Any,
    ) -> None:

        super().__init__(**kwargs)

        self.sepalpha = sepalpha
        self.filetype = filetype
        self.format = format
        self.desc = self.name

    # endregion

    # region Methods

    def process_file_from_pipeline(self, image: PipeImage) -> None:
        if not any(win32_ver()):
            raise UnsupportedPlatformError(
                "TexconvProcessor may only be used on Windows"
            )
        if not which("texconv.exe"):
            raise ExecutableNotFoundError("texcov.exe executable not found in PATH")

        infile = image.last
        outfile = validate_output_path(
            self.pipeline.get_outfile(image, self.suffix, extension="dds")
        )
        if not isfile(outfile):
            self.process_file(
                infile,
                outfile,
                self.pipeline.verbosity,
                sepalpha=self.sepalpha,
                filetype=self.filetype,
                format=self.format,
            )
        image.log(self.name, outfile)

    # endregion

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
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        sepalpha = kwargs.get("sepalpha", False)
        filetype = kwargs.get("filetype")
        format = kwargs.get("format")

        with TemporaryDirectory() as temp_directory:
            tempfile = join(temp_directory, basename(infile))
            copyfile(infile, tempfile)
            command = f"texconv.exe"
            if sepalpha:
                command = f"{command} -sepalpha"
            if filetype:
                command = f"{command} -ft {filetype}"
            if format:
                command = f"{command} -f {format}"
            command = f"{command} -o {temp_directory} {tempfile}"
            if verbosity >= 2:
                print(command)
            Popen(command, shell=True, close_fds=True).wait()
            copyfile(f"{tempfile[:-4]}.dds", outfile)


######################################### MAIN #########################################
if __name__ == "__main__":
    TexconvProcessor.main()
