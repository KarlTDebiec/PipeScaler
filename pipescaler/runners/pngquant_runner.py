#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Runs pngquant tool for reducing image palette."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from shutil import copyfile
from typing import Any

from pipescaler.common import run_command
from pipescaler.core import Runner


class PngquantRunner(Runner):
    """Runs pngquant tool for reducing image palette.

    See [pngquant](https://pngquant.org/).
    """

    def __init__(
        self,
        arguments: str = " --skip-if-larger --force --quality 10-100 --speed 1 --nofs",
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            arguments: Command-line arguments to pass to pngquant
            kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.arguments = arguments

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return f"{self.executable_path} {self.arguments}" " --output {outfile} {infile}"

    def run(self, infile: Path, outfile: Path) -> None:
        """Read image from infile, process it, and save to outfile.

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = self.command_template.format(infile=infile, outfile=outfile)
        debug(f"{self}: {command}")
        exitcode, _, _ = run_command(
            command, acceptable_exitcodes=[0, 98, 99], timeout=self.timeout
        )
        if exitcode in [98, 99]:
            # pngquant may not save outfile if it is too large or low quality
            copyfile(infile, outfile)

    @classmethod
    @property
    def executable(cls) -> str:
        """Name of executable."""
        return "pngquant"

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return "Reduces image palette using [pngquant](https://pngquant.org/)."
