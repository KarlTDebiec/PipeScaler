#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs apngasm."""

from __future__ import annotations

from typing import Any

from pipescaler.core import Runner


class ApngasmRunner(Runner):
    """Runs apngasm tool for creating animated pngs.

    See [apngasm](https://github.com/apngasm/apngasm).
    """

    def __init__(
        self,
        arguments: str = "",
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            arguments: Command-line arguments to pass to apngasm
            **kwargs: Additional keyword arguments
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
            f'"{self.executable_path}" -o {{output_path}} {{input_path}} '
            f"{self.arguments}"
        )

    @classmethod
    def executable(cls) -> str:
        """Name of executable."""
        return "apngasm"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Creates animated pngs using [apngasm](https://github.com/apngasm/apngasm)."
        )
