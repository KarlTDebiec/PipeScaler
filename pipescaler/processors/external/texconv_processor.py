#!/usr/bin/env python
#   pipescaler/processors/external/texconv_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Compresses image using Texconv"""
from __future__ import annotations

from argparse import ArgumentParser
from inspect import cleandoc
from logging import debug
from os.path import basename, dirname, join, splitext
from shutil import copyfile
from typing import Any, Optional, Set

from pipescaler.common import run_command, validate_executable
from pipescaler.core import ExternalProcessor


class TexconvProcessor(ExternalProcessor):
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
            mipmaps: Whether to generate mipmaps
            sepalpha: Whether to generate mips alpha channel separately from color
              channels
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

    @property
    def command_template(self):
        command = f"{validate_executable(self.executable, self.supported_platforms)}"
        if self.mipmaps:
            if self.sepalpha:
                command += " -sepalpha"
        else:
            command += " -m 1"
        if self.filetype:
            command += f" -ft {self.filetype}"
        if self.format:
            command += f" -f {self.format}"
        command += " -o {directory}"
        command += " {infile}"

        return command

    @property
    def executable(self) -> str:
        return "texconv.exe"

    @property
    def supported_platforms(self) -> Set[str]:
        return {"Windows"}

    def process(self, temp_infile: str, temp_outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile
        """
        command = self.command_template.format(
            infile=temp_infile, directory=dirname(temp_outfile)
        )
        debug(f"{self}: {command}")
        run_command(command)
        copyfile(
            join(dirname(temp_outfile), f"{splitext(basename(temp_infile))[0]}.DDS"),
            temp_outfile,
        )

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
    TexconvProcessor.main()
