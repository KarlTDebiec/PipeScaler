#!/usr/bin/env python
#   pipescaler/sources/texmod_source.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Yields images dumped by TexMod"""
from __future__ import annotations

from logging import error

from pipescaler.common import get_name
from pipescaler.sources.directory_source import DirectorySource


class TexmodSource(DirectorySource):
    """Yields images dumped by [TexMod](https://www.moddb.com/downloads/texmod4)"""

    @staticmethod
    def sort(filename):
        """Sort outfiles to be yielded by source"""
        try:
            return int(f"1{int(get_name(filename)[2:10], 16):022d}")
        except ValueError as e:
            error(f"Error encountered while sorting {filename}")
            raise e
