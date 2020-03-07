#!python
# -*- coding: utf-8 -*-
#   filters/ListFilter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import splitext, basename
from typing import Any, Generator, List, Optional

from IPython import embed

from lauhseuisin.filters import Filter


################################### CLASSES ###################################
class ListFilter(Filter):

    def __init__(self, matches: List[str], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.matches = matches

    def __call__(self, downstream_pipes: Optional[
        List[Generator[None, str, None]]] = None) -> Generator[
        None, str, None]:
        while True:
            infile = (yield)
            if self.filter_file(infile):
                if downstream_pipes is not None:
                    for downstream_pipe in downstream_pipes:
                        downstream_pipe.send(infile)

    def filter_file(self, infile: str) -> bool:
        if self.wip_directory in infile:  # Mid-pipe
            embed()
        else:  # Start of pipe
            name = splitext(basename(infile))[0]

        if name not in self.matches:
            return True
        else:
            return False

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Filter]:
        matches = kwargs.pop("matches")
        if not isinstance(matches, list):
            matches = [matches]

        return [cls(matches=matches, **kwargs)]
