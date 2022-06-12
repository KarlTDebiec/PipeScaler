#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Upscales and/or denoises image using Waifu2x via an external executable."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from platform import system

from pipescaler.common import run_command
from pipescaler.core.runner import Runner


class WaifuRunner(Runner):
    """Upscales and/or denoises image using Waifu2x via an external executable.

    See [waifu2x](https://github.com/nagadomi/waifu2x).

    On Windows, requires [waifu2x-caffe](https://github.com/lltcggie/waifu2x-caffe) in
    the executor's path.

    On macOS, requires [waifu2x-mac](https://github.com/imxieyi/waifu2x-mac) in the
    executor's path.
    """

    def __init__(self, arguments: str = "-s 2 -n 1", **kwargs) -> None:
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
            f"{self.executable_path} {self.arguments} "
            f"{'-p gpu' if system()=='Windows' else ''}"
            ' -i "{infile}" -o "{outfile}"'
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

    @classmethod
    @property
    def executable(self) -> str:
        """Name of executable."""
        if system() == "Windows":
            return "waifu2x-caffe-cui.exe"
        return "waifu2x"

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Upscales and/or denoises image using [Waifu2x]"
            "(https://github.com/nagadomi/waifu2x) via an external executable."
        )
