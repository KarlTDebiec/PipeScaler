#!python
#   lauhseuisin/sorters/RegexSorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

import re
from typing import Any, Iterator, List, Optional, Union

from lauhseuisin.sorters.Sorter import Sorter


################################### CLASSES ###################################
class RegexSorter(Sorter):

    def __init__(self, regex: str,
                 downstream_pipes_for_matched: Optional[
                     Union[str, List[str]]] = None,
                 downstream_pipes_for_unmatched: Optional[
                     Union[str, List[str]]] = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.regex = re.compile(regex)
        self.desc = regex

        if isinstance(downstream_pipes_for_matched, str):
            downstream_pipes_for_matched = [downstream_pipes_for_matched]
        self.downstream_pipes_for_matched = downstream_pipes_for_matched

        if isinstance(downstream_pipes_for_unmatched, str):
            downstream_pipes_for_unmatched = [downstream_pipes_for_unmatched]
        self.downstream_pipes_for_unmatched = downstream_pipes_for_unmatched

    def __call__(self) -> Iterator[str]:
        while True:
            infile = (yield)
            if self.regex.match(self.get_original_name(infile)):
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: match {infile}")
                if self.downstream_pipes_for_matched is not None:
                    for pipe in self.downstream_pipes_for_matched:
                        self.pipeline.pipes[pipe].send(infile)
            else:
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: unmatch {infile}")
                if self.downstream_pipes_for_unmatched is not None:
                    for pipe in self.downstream_pipes_for_unmatched:
                        self.pipeline.pipes[pipe].send(infile)
