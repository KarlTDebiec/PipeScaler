#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for executable runners."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from inspect import cleandoc
from logging import debug
from pathlib import Path

from pipescaler.common.subprocess import run_command
from pipescaler.common.validation import val_executable, val_int

__all__ = ["Runner"]


class Runner[InputPath = Path](ABC):
    """Abstract base class for executable runners using Path objects."""

    def __init__(self, timeout: int = 600, *, arguments: Sequence[str] = ()):
        """Validate and store configuration and initialize.

        Arguments:
            timeout: timeout for external tool invocation
            arguments: individual argument tokens, without shell quoting or escaping
        Raises:
            TypeError: if arguments is a command string or contains non-string tokens
        """
        if isinstance(arguments, str) or any(
            not isinstance(argument, str) for argument in arguments
        ):
            raise TypeError("arguments must be a sequence of individual string tokens")
        self.arguments = tuple(arguments)
        """Individual argument tokens passed unchanged to the executable."""
        self.timeout = val_int(timeout, min_value=0)
        self._executable_path: Path | None = None

    def __call__(self, input_path: InputPath, output_path: Path):
        """Run executable on input file, yielding output file.

        Arguments:
            input_path: input file path
            output_path: output file path
        """
        self.run(input_path, output_path)

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        return (
            f"{self.__class__.__name__}(arguments={self.arguments!r}, "
            f"timeout={self.timeout!r})"
        )

    @property
    def executable_path(self) -> Path:
        """Path to executable."""
        if self._executable_path is None:
            self._executable_path = val_executable(
                self.executable(), self.supported_platforms()
            )
        return self._executable_path

    @abstractmethod
    def get_command(self, input_path: InputPath, output_path: Path) -> list[str]:
        """Build an executable argument list without shell parsing.

        Arguments:
            input_path: input path or paths accepted by this runner
            output_path: output file path
        Returns:
            executable followed by individual argument tokens
        """
        raise NotImplementedError()

    def run(self, input_path: InputPath, output_path: Path):
        """Run executable on input file, yielding output file.

        Arguments:
            input_path: input file path
            output_path: output file path
        """
        command = self.get_command(input_path, output_path)
        debug(f"{self}: {command!r}")
        run_command(command, timeout=self.timeout)

    @classmethod
    def executable(cls) -> str:
        """Name of executable.

        Returns:
            name of the external executable
        Raises:
            NotImplementedError: if the subclass does not implement this operation
        """
        raise NotImplementedError()

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links.

        Returns:
            Markdown help describing this component
        """
        if cls.__doc__:
            return cleandoc(cls.__doc__).split(". ", maxsplit=1)[0]
        return ""

    @classmethod
    def supported_platforms(cls) -> set[str]:
        """Platforms on which runner is supported.

        Returns:
            names of platforms supported by this runner
        """
        return {"Darwin", "Linux", "Windows"}
