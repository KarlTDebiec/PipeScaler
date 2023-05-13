#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs potrace tool for tracing images."""
from __future__ import annotations

from pipescaler.core import Runner


class PotraceRunner(Runner):
    """Runs potrace tool for tracing images.

    See [Potrace](http://potrace.sourceforge.net/).
    """

    def __init__(
        self, arguments: str = "-b svg -k 0.3 -a 1.34 -O 0.2", **kwargs
    ) -> None:
        """Initialize.

        Arguments:
            arguments: Command-line arguments to pass to potrace
            kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.arguments = arguments

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(arguments={self.arguments!r})"

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return (
            f"{self.executable_path}" " {infile}" f" {self.arguments}" " -o {outfile}"
        )

    @classmethod
    def executable(cls) -> str:
        """Name of executable."""
        return "potrace"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Traces image using [Potrace](http://potrace.sourceforge.net/) and "
            "re-rasterizes,optionally resizing."
        )
