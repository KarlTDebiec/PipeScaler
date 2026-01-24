#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs pngquant tool for reducing image palette."""

from __future__ import annotations

from logging import debug
from pathlib import Path
from shutil import copyfile
from typing import Any

from pipescaler.common.general import run_command
from pipescaler.core import Runner


class PngquantRunner(Runner):
    """Runs pngquant tool for reducing image palette.

    See [pngquant](https://pngquant.org/).
    """

    def __init__(
        self,
        arguments: str = " --skip-if-larger --force --quality 10-100 --speed 1 --nofs",
        **kwargs: Any,
    ):
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
        return (
            f"{self.executable_path} {self.arguments} "
            f"--output {{output_path}} {{input_path}}"
        )

    def run(self, input_path: Path | str, output_path: Path | str):
        """Read image from input_path, process it, and save to output_path.

        Arguments:
            input_path: Input file path
            output_path: Output file path
        """
        command = self.command_template.format(
            input_path=input_path, output_path=output_path
        )
        debug(f"{self}: {command}")
        exitcode, _, _ = run_command(
            command, acceptable_exitcodes=[0, 98, 99], timeout=self.timeout
        )
        if exitcode in [98, 99]:
            # pngquant may not save output file if it is too large or low quality
            copyfile(input_path, output_path)

    @classmethod
    def executable(cls) -> str:
        """Name of executable."""
        return "pngquant"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return "Reduces image palette using [pngquant](https://pngquant.org/)."
