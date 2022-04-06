#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Yields images dumped by TexMod."""
from __future__ import annotations

from logging import error
from os.path import basename, splitext

from pipescaler.sources.directory_source import DirectorySource


class TexmodSource(DirectorySource):
    """Yields images dumped by TexMod.

    See [TexMod](https://www.moddb.com/downloads/texmod4).
    """

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Yields images dumped by [TexMod](https://www.moddb.com/downloads/texmod4)."
        )

    @staticmethod
    def sort(filename):
        """Sort outfiles to be yielded by source."""
        try:
            return int(f"1{int(splitext(basename(filename))[0][2:10], 16):022d}")
        except ValueError as e:
            error(f"Error encountered while sorting {filename}")
            raise e
