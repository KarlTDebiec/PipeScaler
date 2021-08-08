#!/usr/bin/env python
#   pipescaler/sources/dolphin_source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from logging import error
from os.path import basename, splitext

from pipescaler.sources.directory_source import DirectorySource


####################################### CLASSES ########################################
class DolphinSource(DirectorySource):

    # region Static Methods

    @staticmethod
    def sort(filename):
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
        try:
            return int(f"1{int(width):04d}{int(height):04d}{int(code, 16):022d}")
        except ValueError as e:
            error(f"Error encountered while sorting {filename}")
            raise e

    # endregion
