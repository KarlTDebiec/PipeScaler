#!python
#   lauhseuisin/processors/Processor.py
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
from typing import Any, Iterator, List, Optional, Union

from lauhseuisin.Pipeline import Pipeline


################################### CLASSES ###################################
class Processor(ABC):
    extension: str = "png"
    desc: str = ""

    def __init__(self, pipeline: Pipeline,
                 downstream_pipes: Optional[Union[str, List[str]]] = None,
                 **kwargs: Any) -> None:
        self.pipeline = pipeline

        if isinstance(downstream_pipes, str):
            downstream_pipes = [downstream_pipes]
        self.downstream_pipes = downstream_pipes

    def __call__(self) -> Iterator[str]:
        while True:
            infile = (yield)
            infile = self.backup_infile(infile)
            if self.pipeline.verbosity >= 2:
                print(f"{self}: {infile}")
            outfile = self.get_outfile(infile)
            self.process_file(infile, outfile)
            if self.downstream_pipes is not None:
                for pipe in self.downstream_pipes:
                    self.pipeline.pipes[pipe].send(outfile)

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

    def get_outfile(self, infile: str) -> str:
        original_name = basename(dirname(infile))
        desc_so_far = splitext(basename(infile))[0].lstrip(
            "original")
        outfile = f"{desc_so_far}_{self.desc}.{self.extension}".lstrip("_")
        outfile = f"{self.pipeline.wip_directory}/{original_name}/{outfile}"

        return outfile

    @abstractmethod
    def process_file(self, infile: str, outfile: str) -> None:
        pass
