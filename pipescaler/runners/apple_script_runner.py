#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Runs pngquant tool for reducing image palette."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pipescaler.common import package_root
from pipescaler.core import Runner


class AppleScriptRunner(Runner):
    """Runs pngquant tool for reducing image palette.

    See [pngquant](https://pngquant.org/).
    """

    def __init__(
        self,
        script: Path,
        arguments: str = "",
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration and initialize.

        Args:
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
            script = Path(package_root).joinpath("data", "scripts")
        if not script.exists():
            raise ValueError()
        if not script.is_dir():
            raise ValueError()
        self.script = script

        self.arguments = arguments

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return (
            f"{self.executable_path} {self.script}" ' "{infile}" ' f"{self.arguments}"
        )

    @classmethod
    @property
    def executable(self) -> str:
        """Name of executable."""
        return "osascript"

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Runs image through an [AppleScript]"
            "(https://developer.apple.com/library/archive/documentation/AppleScript/"
            "Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html), "
            "using an application such as [Pixelmator Pro]"
            "(https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)."
        )

    @classmethod
    @property
    def supported_platforms(self) -> set[str]:
        """Platforms on which runner is supported."""
        return {"Darwin"}
