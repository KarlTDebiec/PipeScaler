#!/usr/bin/env python
#   pipescaler/sources/citra_source.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from pipescaler.common import get_name
from pipescaler.core import Source


####################################### CLASSES ########################################
class CitraSource(Source):

    # region Static Methods

    @staticmethod
    def sort(filename):
        _, size, code, _ = get_name(filename).split("_")
        width, height = size.split("x")
        return int(f"1{int(width):04d}{int(height):04d}{int(code, 16):022d}")

    # endregion
