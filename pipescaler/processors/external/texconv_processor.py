#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Processes image using Texconv."""
from __future__ import annotations

from logging import debug
from os.path import basename, dirname, join, splitext
from shutil import copyfile
from typing import Optional

from pipescaler.common import run_command, validate_executable
from pipescaler.core.stages.processors import ExternalProcessor


class TexconvProcessor(ExternalProcessor):
    """Processes image using Texconv.

    See [Texconv](https://github.com/Microsoft/DirectXTex/wiki/Texconv).
    """

    extension = "dds"

    def __init__(
        self,
        mipmaps: bool = False,
        sepalpha: bool = False,
        filetype: Optional[str] = "DDS",
        format: Optional[str] = "BC7_UNORM",
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            mipmaps: Whether to generate mipmaps
            sepalpha: Whether to generate mips alpha channel separately from color
              channels
            filetype: Output file type
            format: Output format
        """
        self.mipmaps = mipmaps
        self.sepalpha = sepalpha
        self.filetype = filetype
        self.format = format

    @property
    def command_template(self):
        """String template with which to generate command."""
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

    def process(self, infile: str, outfile: str) -> None:
        """Read image from infile, process it, and save to outfile.

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = self.command_template.format(
            infile=infile, directory=dirname(outfile)
        )
        debug(f"{self}: {command}")
        run_command(command)
        copyfile(
            join(dirname(outfile), f"{splitext(basename(infile))[0]}.DDS"),
            outfile,
        )

    @classmethod
    @property
    def executable(self) -> str:
        """Name of executable."""
        return "texconv.exe"

    @classmethod
    @property
    def supported_platforms(self) -> set[str]:
        """Platforms on which processor is supported."""
        return {"Windows"}

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Processes image using [Texconv]"
            "(https://github.com/Microsoft/DirectXTex/wiki/Texconv)."
        )
