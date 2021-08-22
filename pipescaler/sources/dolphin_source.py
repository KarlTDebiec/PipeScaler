#!/usr/bin/env python
#   pipescaler/sources/dolphin_source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from logging import error
from os.path import basename, splitext

from pipescaler.sources.directory_source import DirectorySource


class DolphinSource(DirectorySource):

    # region Static Methods

    @staticmethod
    def sort(filename):
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

    # endregion
