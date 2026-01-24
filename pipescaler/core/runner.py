#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for executable runners."""

from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import cleandoc
from logging import debug
from pathlib import Path

from pipescaler.common.general import run_command
from pipescaler.common.validation import val_executable, val_int


class Runner(ABC):
    """Abstract base class for executable runners."""

    def __init__(self, timeout: int = 600):
        """Validate and store configuration and initialize.

        Arguments:
            timeout: Timeout for external tool invocation
        """
        self.timeout = val_int(timeout, min_value=0)
        self._executable_path: Path | None = None

    def __call__(self, input_path: Path | str, output_path: Path | str):
        """Run executable on input file, yielding output file.

        Arguments:
            input_path: Input file path
            output_path: Output file path
        """
        self.run(input_path, output_path)

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(timeout={self.timeout!r})"

    @property
    @abstractmethod
    def command_template(self) -> str:
        """String template with which to generate command."""
        raise NotImplementedError()

    @classmethod
    def executable(cls) -> str:
        """Name of executable."""
        raise NotImplementedError()

    @property
    def executable_path(self) -> Path:
        """Path to executable."""
        if self._executable_path is None:
            self._executable_path = Path(
                val_executable(self.executable(), self.supported_platforms())
            )
        return self._executable_path

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

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        if cls.__doc__:
            return cleandoc(cls.__doc__).split(". ", maxsplit=1)[0]
        return ""

    @classmethod
    def supported_platforms(cls) -> set[str]:
        """Platforms on which runner is supported."""
        return {"Darwin", "Linux", "Windows"}
