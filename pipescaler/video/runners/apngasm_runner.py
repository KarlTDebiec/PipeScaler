#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs apngasm."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pipescaler.core import Runner

__all__ = ["ApngasmRunner"]


class ApngasmRunner(Runner[Path | Sequence[Path]]):
    """Runs apngasm tool for creating animated pngs.

    See [apngasm](https://github.com/apngasm/apngasm).
    """

    def __init__(
        self,
        arguments: Sequence[str] = (),
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            arguments: individual argument tokens to pass to apngasm without quoting
            **kwargs: Additional keyword arguments
        """
        super().__init__(arguments=arguments, **kwargs)

    def get_command(
        self, input_path: Path | Sequence[Path], output_path: Path
    ) -> list[str]:
        """Build the apngasm argument list for one or more input frames.

        Arguments:
            input_path: one frame path or an ordered sequence of frame paths
            output_path: output animated image path
        Returns:
            executable and individual argument tokens
        Raises:
            ValueError: if no input frame paths are provided
        """
        if isinstance(input_path, Path):
            input_paths = [input_path]
        else:
            input_paths = input_path
        if not input_paths:
            raise ValueError("At least one input frame path is required")
        return [
            str(self.executable_path),
            "-o",
            str(output_path),
            *(str(path) for path in input_paths),
            *self.arguments,
        ]

    @classmethod
    def executable(cls) -> str:
        """Name of executable.

        Returns:
            absolute path of the external executable
        """
        return "apngasm"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links.

        Returns:
            Markdown help describing this component
        """
        return (
            "Creates animated pngs using [apngasm](https://github.com/apngasm/apngasm)."
        )
