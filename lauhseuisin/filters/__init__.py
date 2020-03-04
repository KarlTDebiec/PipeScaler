#!python
# -*- coding: utf-8 -*-
#   filters/__init__.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generator, List, Optional


################################### CLASSES ###################################
class Filter(ABC):

    def __init__(self, **kwargs: Any) -> None:
        pass

    def __call__(self, downstream_pipes: Optional[List[
        Generator[None, str, None]]] = None) -> Generator[None, str, None]:
        while True:
            infile = (yield)
            self.filter_file(infile)
            if downstream_pipes is not None:
                for downstream_pipe in downstream_pipes:
                    downstream_pipe.send(infile)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return self.__repr__()

    @abstractmethod
    def filter_file(self, infile: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def get_pipes(cls, **kwargs: Any) -> List[Filter]:
        pass

from lauhseuisin.filters.RegexFilter import RegexFilter
from lauhseuisin.filters.TextImageFilter import TextImageFilter
