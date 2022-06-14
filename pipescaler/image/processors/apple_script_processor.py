#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Runs image through an AppleScript."""
from __future__ import annotations

from os.path import join, split
from typing import Any

from pipescaler.common import package_root, validate_executable, validate_input_path
from pipescaler.core.image import Processor


class AppleScriptProcessor(Processor):
    """Runs image through an AppleScript.

    See [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html),
    and [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)
    """

    def __init__(self, script: str, args: str = "", **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            script: Path to AppleScript to run
            args: Arguments to pass to AppleScript
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        if not script.endswith(".scpt"):
            script = f"{script}.scpt"
        self.script = validate_input_path(
            script,
            default_directory=join(*split(package_root), "data", "../../data/scripts"),
        )
        self.args = args

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return (
            f"{validate_executable(self.executable, self.supported_platforms)}"
            f' "{self.script}"'
            ' "{infile}"'
            f" {self.args}"
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
        """Platforms on which processor is supported."""
        return {"Darwin"}
