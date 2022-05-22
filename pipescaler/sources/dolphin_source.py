#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Yields images dumped by Dolphin."""
from __future__ import annotations

from logging import error
from os.path import basename, splitext

from pipescaler.sources.directory_source import DirectorySource


class DolphinSource(DirectorySource):
    """Yields images dumped by Dolphin.

    See [Dolphin](https://dolphin-emu.org/)
    """

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return "Yields images dumped by [Dolphin](https://dolphin-emu.org/)."

    @staticmethod
    def sort(filename):
        """Sort outfiles to be yielded by source."""
        try:
            components = splitext(basename(filename))[0].split("_")
            if len(components) == 4:
                size = components[1]
                code = components[2]
            elif len(components) == 5:
                size = components[1]
                code = components[3]
            elif len(components) == 6:
                size = components[1]
                code = components[3]
            else:
                raise ValueError()
            width, height = size.split("x")

            return int(f"1{int(width):04d}{int(height):04d}{int(code, 16):022d}")
        except ValueError as e:
            error(f"Error encountered while sorting {filename}")
            raise e
