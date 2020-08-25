#!/usr/bin/env python
#   pipescaler/sources/citra_dump_source.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os import listdir
from os.path import expandvars, join
from typing import Any, Iterator

from pipescaler.sources.source import Source


####################################### CLASSES ########################################
class CitraDumpSource(Source):
    def __init__(self, input_directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.input_directory = expandvars(input_directory)
        self.desc = self.input_directory

    def get_infiles(self) -> Iterator[str]:
        infiles = listdir(self.input_directory)
        infiles.sort(key=self.name_sort)
        for i, infile in enumerate(infiles):
            print(f"Processing {i}/{len(infiles)}: {infile}")
            if infile == ".DS_Store":
                continue
            yield join(self.input_directory, infile)

    @staticmethod
    def name_sort(filename):
        if filename == ".DS_Store":
            return 0
        _, size, code, _ = filename.split("_")
        width, height = size.split("x")
        return int(f"1{int(width):04d}{int(height):04d}{int(code, 16):022d}")
