#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Processes image using Texconv."""
from __future__ import annotations

from logging import debug
from os import rename
from pathlib import Path

from pipescaler.common import run_command
from pipescaler.core.runner import Runner


class TexconvRunner(Runner):
    """Processes image using Texconv.

    See [Texconv](https://github.com/Microsoft/DirectXTex/wiki/Texconv).
    """

    def __init__(
        self, arguments: str = "-y -sepalpha -m 1 -ft DDS -f BC7_UNORM", **kwargs
    ) -> None:
        """Store configuration.

        Arguments:
            arguments: Additional arguments to provide at the command line
            kwargs: Additional arguments
        """
        super().__init__(**kwargs)

        self.arguments = arguments

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return (
            f"{self.executable_path} {self.arguments}" " -o {outfile.parent} {infile}"
        )

    def run(self, infile: Path, outfile: Path) -> None:
        """Read image from infile, process it, and save to outfile.

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = self.command_template.format(infile=infile, outfile=outfile)
        debug(f"{self}: {command}")
        run_command(command, timeout=self.timeout)
        rename(outfile.with_stem(infile.stem), outfile)

    @classmethod
    @property
    def executable(self) -> str:
        """Name of executable."""
        return "texconv.exe"

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Processes image using [Texconv]"
            "(https://github.com/Microsoft/DirectXTex/wiki/Texconv)."
        )

    @classmethod
    @property
    def supported_platforms(self) -> set[str]:
        """Platforms on which processor is supported."""
        return {"Windows"}
