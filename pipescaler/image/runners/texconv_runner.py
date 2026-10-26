#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs texconv tool for converting image format."""

from __future__ import annotations

from collections.abc import Sequence
from logging import debug
from os import rename
from pathlib import Path
from typing import Any

from pipescaler.common.subprocess import run_command
from pipescaler.core import Runner

__all__ = ["TexconvRunner"]


class TexconvRunner(Runner):
    """Runs texconv tool for converting image format.

    See [Texconv](https://github.com/Microsoft/DirectXTex/wiki/Texconv).
    """

    def __init__(
        self,
        arguments: Sequence[str] = ("-y", "-sepalpha", "-ft", "DDS", "-f", "BC7_UNORM"),
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            arguments: individual argument tokens to pass to texconv without quoting
            **kwargs: Additional keyword arguments
        """
        super().__init__(arguments=arguments, **kwargs)

    def get_command(self, input_path: Path | str, output_path: Path | str) -> list[str]:
        """Build the texconv argument list.

        Arguments:
            input_path: input image path
            output_path: output image path
        Returns:
            executable and individual argument tokens
        """
        return [
            str(self.executable_path),
            *self.arguments,
            "-o",
            str(Path(output_path).parent),
            str(input_path),
        ]

    def run(self, input_path: Path | str, output_path: Path | str):
        """Run executable on input file, yielding output file.

        Arguments:
            input_path: Input file path
            output_path: Output file path
        """
        command = self.get_command(input_path, output_path)
        debug(f"{self}: {command!r}")
        run_command(command, timeout=self.timeout)
        rename(Path(output_path).with_stem(Path(input_path).stem), output_path)

    @classmethod
    def executable(cls) -> str:
        """Name of executable.

        Returns:
            absolute path of the external executable
        """
        return "texconv.exe"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links.

        Returns:
            Markdown help describing this component
        """
        return (
            "Processes image using [Texconv]"
            "(https://github.com/Microsoft/DirectXTex/wiki/Texconv)."
        )

    @classmethod
    def supported_platforms(cls) -> set[str]:
        """Platforms on which runner is supported.

        Returns:
            names of platforms supported by this runner
        """
        return {"Windows"}
