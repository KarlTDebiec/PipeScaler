#!/usr/bin/env python
#   pipescaler/sources/citra_source.py
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


class CitraSource(DirectorySource):
    @staticmethod
    def sort(filename):
        try:
            _, size, code, _ = splitext(basename(filename))[0].split("_")
            width, height = size.split("x")
            return int(f"1{int(width):04d}{int(height):04d}{int(code, 16):022d}")
        except ValueError as e:
            error(f"Error encountered while sorting {filename}")
            raise e
