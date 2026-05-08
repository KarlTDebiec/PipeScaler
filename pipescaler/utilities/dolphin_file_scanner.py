#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Scans Dolphin dump directories for new files."""

from __future__ import annotations

from re import compile

from .file_scanner import FileScanner


class DolphinFileScanner(FileScanner):
    """Scans Dolphin dump directories for new files."""

    _mip_regex = compile(r"^.+_mip\d+$")

    def get_operation(self, name: str) -> str:
        """Select operation for filename.

        Arguments:
            name: name of file
        Returns:
            operation to perform
        """
        if self._mip_regex.match(name):
            return "ignore"
        return super().get_operation(name)
