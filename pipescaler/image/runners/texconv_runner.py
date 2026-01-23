#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs texconv tool for converting image format."""

from __future__ import annotations

from logging import debug
from os import rename
from pathlib import Path

from pipescaler.common.general import run_command
from pipescaler.core import Runner


class TexconvRunner(Runner):
    """Runs texconv tool for converting image format.

    See [Texconv](https://github.com/Microsoft/DirectXTex/wiki/Texconv).
    """

    def __init__(self, arguments: str = "-y -sepalpha -ft DDS -f BC7_UNORM", **kwargs):
        """Initialize.

        Arguments:
            arguments: Command-line arguments to pass to texconv
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
            f"{self.executable_path} {self.arguments}"
            ' -o "{output_path.parent}" "{input_path}"'
        )

    def run(self, input_path: Path | str, output_path: Path | str):
        """Run executable on input file, yielding output file.

        Arguments:
            input_path: Input file path
            output_path: Output file path
        """
        command = self.command_template.format(
            input_path=input_path, output_path=output_path
        )
        debug(f"{self}: {command}")
        run_command(command, timeout=self.timeout)
        rename(Path(output_path).with_stem(Path(input_path).stem), output_path)

    @classmethod
    def executable(cls) -> str:
        """Name of executable."""
        return "texconv.exe"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Processes image using [Texconv]"
            "(https://github.com/Microsoft/DirectXTex/wiki/Texconv)."
        )

    @classmethod
    def supported_platforms(cls) -> set[str]:
        """Platforms on which runner is supported."""
        return {"Windows"}
