#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Traces image using potrace and re-rasterizes, optionally resizing."""
from __future__ import annotations

from logging import debug
from pathlib import Path

from pipescaler.common import run_command
from pipescaler.core.runner import Runner


class PotraceRunner(Runner):
    """Traces image using potrace and re-rasterizes, optionally resizing.

    See [Potrace](http://potrace.sourceforge.net/).
    """

    def __init__(
        self, arguments: str = "-b svg -k 0.3 -a 1.34 -O 0.2", **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.arguments = arguments

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return f"{self.executable_path}" " {infile}" f"{self.arguments}" " -o {outfile}"

    def run(self, infile: Path, outfile: Path) -> None:
        command = self.command_template.format(infile=infile, outfile=outfile)
        debug(f"{self}: {command}")
        run_command(command, timeout=self.timeout)

    @classmethod
    @property
    def executable(self) -> str:
        """Name of executable."""
        return "potrace"

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Traces image using [Potrace](http://potrace.sourceforge.net/) and "
            "re-rasterizes,optionally resizing."
        )
