#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Runs pngquant tool for reducing image palette."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from shutil import copyfile
from typing import Any

from pipescaler.common import DirectoryNotFoundError, package_root, run_command
from pipescaler.core import Runner


class AutomatorRunner(Runner):
    """Runs pngquant tool for reducing image palette.

    See [pngquant](https://pngquant.org/).
    """

    def __init__(
        self,
        workflow: Path,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Args:
            workflow: Workflow to run
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        if not isinstance(workflow, Path):
            workflow = Path(workflow)
        if workflow.suffix != ".workflow":
            workflow = workflow.with_suffix(".workflow")
        if not workflow.is_absolute():
            workflow = package_root.joinpath("data", "workflows", workflow)
        if not workflow.exists():
            raise DirectoryNotFoundError()
        if not workflow.is_dir():
            raise DirectoryNotFoundError()
        self.workflow = workflow

    def run(self, infile: Path, outfile: Path) -> None:
        """Run executable on infile, yielding outfile.

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = self.command_template.format(infile=infile, outfile=outfile)
        debug(f"{self}: {command}")
        run_command(command, timeout=self.timeout)
        copyfile(infile, outfile)

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return f"{self.executable_path}" " -i {infile}" f" {self.workflow}"

    @classmethod
    @property
    def executable(self) -> str:
        """Name of executable."""
        return "automator"

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Applies an [Automator QuickAction]"
            "(https://support.apple.com/guide/automator/welcome/mac) "
            "to an image; for example using [Pixelmator Pro]"
            "(https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)."
        )

    @classmethod
    @property
    def supported_platforms(self) -> set[str]:
        """Platforms on which runner is supported."""
        return {"Darwin"}
