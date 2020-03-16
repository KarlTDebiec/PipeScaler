#!python
#   lauhseuisin/processors/Source.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterator, List, Optional, Union

from lauhseuisin.Pipeline import Pipeline


################################### CLASSES ###################################
class Source(ABC):
    desc: str = ""

    def __init__(self, pipeline: Pipeline,
                 downstream_pipes: Optional[Union[str, List[str]]] = None,
                 **kwargs: Any) -> None:
        self.pipeline = pipeline
        if isinstance(downstream_pipes, str):
            downstream_pipes = [downstream_pipes]
        self.downstream_pipes = downstream_pipes

    def __call__(self) -> None:
        for infile in self.get_infiles():
            if self.pipeline.verbosity >= 2:
                print(f"{self}: {infile}")
            if self.downstream_pipes is not None:
                for pipe in self.downstream_pipes:
                    self.pipeline.pipes[pipe].send(infile)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.desc}>"

    def __str__(self) -> str:
        return self.__repr__()

    @abstractmethod
    def get_infiles(self) -> Iterator[str]:
        pass
