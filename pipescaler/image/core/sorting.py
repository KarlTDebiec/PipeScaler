#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Functions for sorting."""
from __future__ import annotations

from logging import error
from os.path import basename, splitext


def citra_sort(filename: str) -> int:
    """Sort filenames dumped by Citra.

    See [Citra](https://citra-emu.org)
    """
    try:
        _, size, code, _ = splitext(basename(filename))[0].split("_")
        width, height = size.split("x")
        return int(f"1{int(width):04d}{int(height):04d}{int(code, 16):022d}")
    except ValueError as e:
        error(f"Error encountered while sorting {filename}")
        raise e


def dolphin_sort(filename: str) -> int:
    """Sort filenames dumped by Dolphin.

    See [Dolphin](https://dolphin-emu.org/).
    """
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


def texmod_sort(filename: str) -> int:
    """Sort filenames dumped by TexMod.

    See [TexMod](https://www.moddb.com/downloads/texmod4).
    """
    try:
        return int(f"1{int(splitext(basename(filename))[0][2:10], 16):022d}")
    except ValueError as e:
        error(f"Error encountered while sorting {filename}")
        raise e
