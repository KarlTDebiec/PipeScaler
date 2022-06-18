#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import cleandoc
from logging import debug
from pathlib import Path

from pipescaler.common import run_command, validate_executable, validate_int


class Runner(ABC):
    def __init__(self, timeout: int = 600) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            timeout: Timeout for external tool invocation
        """
        self.timeout = validate_int(timeout, 0)
        self._executable_path = None

    @property
    @abstractmethod
    def command_template(self) -> str:
        """String template with which to generate command."""
        raise NotImplementedError()

    @property
    def executable_path(self) -> Path:
        """Path to executable."""
        if self._executable_path is None:
            self._executable_path = Path(
                validate_executable(self.executable, self.supported_platforms)
            )
        return self._executable_path

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
        raise NotImplementedError()

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        if cls.__doc__:
            return cleandoc(cls.__doc__).split(". ", maxsplit=1)[0]
        return ""

    @classmethod
    @property
    def supported_platforms(self) -> set[str]:
        """Platforms on which processor is supported."""
        return {"Darwin", "Linux", "Windows"}
