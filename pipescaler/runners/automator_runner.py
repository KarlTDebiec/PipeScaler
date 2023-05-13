#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs an Automator QuickAction."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from shutil import copyfile
from typing import Any

from pipescaler.common import (
    DirectoryNotFoundError,
    PathLike,
    package_root,
    run_command,
)
from pipescaler.core import Runner


class AutomatorRunner(Runner):
    """Runs an Automator QuickAction.

    See [Automator QuickAction](https://support.apple.com/guide/automator/welcome/mac).
    """

    def __init__(
        self,
        workflow: Path,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            workflow: Workflow to run
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        if not isinstance(workflow, Path):
            workflow = Path(workflow)
        if workflow.suffix != ".workflow":
            workflow = workflow.with_suffix(".workflow")
        if not workflow.is_absolute():
            workflow = package_root / "image/data/workflows" / workflow
        if not workflow.exists():
            raise DirectoryNotFoundError()
        if not workflow.is_dir():
            raise DirectoryNotFoundError()
        self.workflow = workflow

    def run(self, infile: PathLike, outfile: PathLike) -> None:
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
    def executable(cls) -> str:
        """Name of executable."""
        return "automator"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Applies an [Automator QuickAction]"
            "(https://support.apple.com/guide/automator/welcome/mac) "
            "to an image; for example using [Pixelmator Pro]"
            "(https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)."
        )

    @classmethod
    def supported_platforms(cls) -> set[str]:
        """Platforms on which runner is supported."""
        return {"Darwin"}
