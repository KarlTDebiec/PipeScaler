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
from os.path import basename, dirname, splitext
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

    def get_original_name(self, infile: str):
        if self.pipeline.wip_directory in infile:
            return basename(dirname(infile))
        else:
            return splitext(basename(infile))[0]
