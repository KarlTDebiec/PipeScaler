#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs pngquant tool for reducing image palette."""
from __future__ import annotations

from logging import debug
from shutil import copyfile
from typing import Any

from pipescaler.common import PathLike, run_command
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
        """Initialize.

        Arguments:
            arguments: Command-line arguments to pass to pngquant
            kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.arguments = arguments

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(arguments={self.arguments!r})"

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return f"{self.executable_path} {self.arguments}" " --output {outfile} {infile}"

    def run(self, infile: PathLike, outfile: PathLike) -> None:
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
    def executable(cls) -> str:
        """Name of executable."""
        return "pngquant"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return "Reduces image palette using [pngquant](https://pngquant.org/)."
