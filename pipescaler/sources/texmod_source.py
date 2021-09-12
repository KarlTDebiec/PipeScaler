#!/usr/bin/env python
#   pipescaler/sources/texmod_source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from logging import error

from pipescaler.common import get_name
from pipescaler.sources import DirectorySource


class TexmodSource(DirectorySource):
    @staticmethod
    def sort(filename):
        try:
            return int(f"1{int(get_name(filename)[2:10], 16):022d}")
        except ValueError as e:
            error(f"Error encountered while sorting {filename}")
            raise e
