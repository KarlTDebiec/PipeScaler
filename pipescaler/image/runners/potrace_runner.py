#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs potrace tool for tracing images."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pipescaler.core import Runner

__all__ = ["PotraceRunner"]


class PotraceRunner(Runner):
    """Runs potrace tool for tracing images.

    See [Potrace](http://potrace.sourceforge.net/).
    """

    def __init__(
        self,
        arguments: Sequence[str] = (
            "-b",
            "svg",
            "-k",
            "0.3",
            "-a",
            "1.34",
            "-O",
            "0.2",
        ),
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            arguments: individual argument tokens to pass to potrace without quoting
            **kwargs: Additional keyword arguments
        """
        super().__init__(arguments=arguments, **kwargs)

    def get_command(self, input_path: Path, output_path: Path) -> list[str]:
        """Build the potrace argument list.

        Arguments:
            input_path: input image path
            output_path: output vector image path
        Returns:
            executable and individual argument tokens
        """
        return [
            str(self.executable_path),
            str(input_path),
            *self.arguments,
            "-o",
            str(output_path),
        ]

    @classmethod
    def executable(cls) -> str:
        """Name of executable.

        Returns:
            absolute path of the external executable
        """
        return "potrace"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links.

        Returns:
            Markdown help describing this component
        """
        return (
            "Traces image using [Potrace](http://potrace.sourceforge.net/) and "
            "re-rasterizes,optionally resizing."
        )
