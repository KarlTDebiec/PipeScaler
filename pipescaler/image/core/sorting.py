#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for sorting."""

from __future__ import annotations

import re
from logging import error
from os.path import basename, splitext

# tex1_8x8_0EAEA8971E8954F4_13_mip0.png
# tex1_32x32_0A4B083BF0B35A78_12.png


_CITRA_STEM_RE = re.compile(
    r"^tex\d+_(?P<w>\d+)x(?P<h>\d+)_(?P<code>[0-9A-Fa-f]+)_(?P<idx>\d+)(?:_mip\d+)?$"
)


def citra_sort(filename: str) -> int:
    """Sort filenames dumped by Citra.

    Supports:
      - tex1_32x32_0A4B083BF0B35A78_12.png
      - tex1_8x8_0EAEA8971E8954F4_13_mip0.png
    """
    stem = splitext(basename(filename))[0]
    m = _CITRA_STEM_RE.match(stem)
    if not m:
        error(f"Error encountered while sorting {filename}")
        raise ValueError(f"Unrecognized Citra filename pattern: {filename}")

    width = int(m["w"])
    height = int(m["h"])
    code = int(m["code"], 16)
    # Keep same ordering semantics as before: width, height, then code (ignore idx/mip)
    return int(f"1{width:04d}{height:04d}{code:022d}")


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
