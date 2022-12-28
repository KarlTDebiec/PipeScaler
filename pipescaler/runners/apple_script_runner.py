#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Runs an AppleScript."""
from __future__ import annotations

from logging import debug
from pathlib import Path
from shutil import copyfile
from typing import Any

from pipescaler.common import package_root, run_command
from pipescaler.core import Runner


# pylint: disable=line-too-long
class AppleScriptRunner(Runner):
    """Runs an AppleScript.

    See [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html).
    """

    def __init__(
        self,
        script: Path,
        arguments: str = "",
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            script: AppleScript to run
            arguments: Arguments to pass to AppleScript
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        if not isinstance(script, Path):
            script = Path(script)
        if script.suffix != ".scpt":
            script = script.with_suffix(".scpt")
        if not script.is_absolute():
            script = package_root / "data" / "scripts" / script
        if not script.exists():
            raise FileNotFoundError()
        if not script.is_file():
            raise FileNotFoundError()
        self.script = script

        self.arguments = arguments

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return (
            f"{self.executable_path} {self.script}" ' "{infile}" ' f"{self.arguments}"
        )

    @classmethod
    def executable(cls) -> str:
        """Name of executable."""
        return "osascript"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Runs image through an [AppleScript]"
            "(https://developer.apple.com/library/archive/documentation/AppleScript/"
            "Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html), "
            "using an application such as [Pixelmator Pro]"
            "(https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)."
        )

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

    @classmethod
    def supported_platforms(cls) -> set[str]:
        """Platforms on which runner is supported."""
        return {"Darwin"}
