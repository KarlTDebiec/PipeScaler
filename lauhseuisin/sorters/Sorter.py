#!python
#   lauhseuisin/sorters/Sorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from abc import ABC, abstractmethod
from os import makedirs
from os.path import basename, dirname, isdir, splitext
from shutil import copyfile
from typing import Any, Iterator

from lauhseuisin.Pipeline import Pipeline


################################### CLASSES ###################################
class Sorter(ABC):
    desc: str = ""

    def __init__(self, pipeline: Pipeline, **kwargs: Any) -> None:
        self.pipeline = pipeline

    @abstractmethod
    def __call__(self) -> Iterator[str]:
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.desc}>"

    def __str__(self) -> str:
        return self.__repr__()

    def backup_infile(self, infile: str) -> str:
        if self.pipeline.wip_directory not in infile:
            name = splitext(basename(infile))[0]
            ext = splitext(infile)[1]
            if not isdir(f"{self.pipeline.wip_directory}/{name}"):
                makedirs(f"{self.pipeline.wip_directory}/{name}")
            new_infile = f"{self.pipeline.wip_directory}/{name}/original{ext}"
            copyfile(infile, new_infile)

            return new_infile
        else:
            return infile

    def get_original_name(self, infile: str) -> str:
        if self.pipeline.wip_directory in infile:
            return basename(dirname(infile))
        else:
            return splitext(basename(infile))[0]

    def log_outfile(self, outfile: str) -> None:
        name = self.get_original_name(outfile)
        if name not in self.pipeline.log:
            self.pipeline.log[name] = [basename(outfile)]
        else:
            self.pipeline.log[name].append(basename(outfile))
