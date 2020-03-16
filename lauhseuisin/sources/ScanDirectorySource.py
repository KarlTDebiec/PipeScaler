#!python
#   lauhseuisin/sources/ScanDirectorySource.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os import listdir
from os.path import expandvars, join
from typing import Any, Iterator

from lauhseuisin.sources.Source import Source


################################### CLASSES ###################################
class ScanDirectorySource(Source):

    def __init__(self, input_directory: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.input_directory = expandvars(input_directory)
        self.desc = self.input_directory

    def get_infiles(self) -> Iterator[str]:
        for infile in listdir(self.input_directory):
            if infile == ".DS_Store":
                continue
            yield join(self.input_directory, infile)
