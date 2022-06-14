#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Applies an Automator QuickAction to an image."""
from __future__ import annotations

from os.path import join, split
from typing import Any

from pipescaler.common import package_root, validate_executable, validate_input_path
from pipescaler.core.image import Processor


class AutomatorProcessor(Processor):
    """Applies an Automator QuickAction to an image.

    See [Automator QuickAction](https://support.apple.com/guide/automator/welcome/mac)
    and [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)
    """

    def __init__(self, workflow: str, **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            workflow: Automator workflow to run
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.workflow = validate_input_path(
            workflow if workflow.endswith(".workflow") else f"{workflow}.workflow",
            file_ok=False,
            directory_ok=True,
            default_directory=join(
                *split(package_root), "data", "../../data/workflows"
            ),
        )

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return (
            f"{validate_executable(self.executable, self.supported_platforms)}"
            " -i {infile}"
            f" {self.workflow}"
        )

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
        """Platforms on which processor is supported."""
        return {"Darwin"}
