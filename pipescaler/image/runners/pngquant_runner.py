#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs pngquant tool for reducing image palette."""

from __future__ import annotations

from collections.abc import Sequence
from logging import debug
from pathlib import Path
from shutil import copyfile
from typing import Any

from pipescaler.common.subprocess import run_command
from pipescaler.core import Runner

__all__ = ["PngquantRunner"]


class PngquantRunner(Runner):
    """Runs pngquant tool for reducing image palette.

    See [pngquant](https://pngquant.org/).
    """

    def __init__(
        self,
        arguments: Sequence[str] = (
            "--skip-if-larger",
            "--force",
            "--quality",
            "10-100",
            "--speed",
            "1",
            "--nofs",
        ),
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            arguments: individual argument tokens to pass to pngquant without quoting
            **kwargs: Additional keyword arguments
        """
        super().__init__(arguments=arguments, **kwargs)

    def get_command(self, input_path: Path, output_path: Path) -> list[str]:
        """Build the pngquant argument list.

        Arguments:
            input_path: input image path
            output_path: output image path
        Returns:
            executable and individual argument tokens
        """
        return [
            str(self.executable_path),
            *self.arguments,
            "--output",
            str(output_path),
            str(input_path),
        ]

    def run(self, input_path: Path, output_path: Path):
        """Read image from input_path, process it, and save to output_path.

        Arguments:
            input_path: input file path
            output_path: output file path
        """
        command = self.get_command(input_path, output_path)
        debug(f"{self}: {command!r}")
        exitcode, _, _ = run_command(
            command, acceptable_exitcodes=[0, 98, 99], timeout=self.timeout
        )
        if exitcode in [98, 99]:
            # pngquant may not save output file if it is too large or low quality
            copyfile(input_path, output_path)

    @classmethod
    def executable(cls) -> str:
        """Name of executable.

        Returns:
            absolute path of the external executable
        """
        return "pngquant"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links.

        Returns:
            Markdown help describing this component
        """
        return "Reduces image palette using [pngquant](https://pngquant.org/)."
