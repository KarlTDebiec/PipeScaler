#!python
# -*- coding: utf-8 -*-
#   processors/__init__.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from abc import ABC, abstractmethod
from os.path import basename, dirname, expandvars, splitext
from shutil import which
from typing import Any, Generator, List, Optional


################################### CLASSES ###################################
class Processor(ABC):
    executable_name: Optional[str] = None
    extension: str = "png"

    def __init__(self, **kwargs: Any) -> None:
        self.paramstring = kwargs.get("paramstring", None)
        if self.executable_name is not None:
            self.executable = expandvars(
                str(kwargs.get("executable", which(self.executable_name))))

    def __call__(self, downstream_processors: Optional[List[
        Generator[None, str, None]]] = None) -> Generator[None, str, None]:
        while True:
            infile = (yield)
            outfile = self.get_outfile(infile)
            self.process_file(infile, outfile)
            if downstream_processors is not None:
                for downstream_processor in downstream_processors:
                    downstream_processor.send(outfile)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.paramstring}>"

    def __str__(self) -> str:
        return self.__repr__()

    def get_outfile(self, infile: str) -> str:
        outfile = splitext(basename(infile))[0].lstrip("original")
        if self.paramstring != "":
            outfile += f"_{self.paramstring}"
        outfile = outfile.lstrip("_")
        outfile += f".{self.extension}"
        return f"{dirname(infile)}/{outfile}"

    @abstractmethod
    def process_file(self, infile: str, outfile: str) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        pass


from lauhseuisin.processors.AutomatorProcessor import AutomatorProcessor
from lauhseuisin.processors.CopyProcessor import CopyProcessor
from lauhseuisin.processors.FlattenProcessor import FlattenProcessor
from lauhseuisin.processors.ImageMagickProcessor import ImageMagickProcessor
from lauhseuisin.processors.ResizeProcessor import ResizeProcessor
from lauhseuisin.processors.ThresholdProcessor import ThresholdProcessor
from lauhseuisin.processors.WaifuProcessor import WaifuProcessor
from lauhseuisin.processors.XbrzProcessor import XbrzProcessor
