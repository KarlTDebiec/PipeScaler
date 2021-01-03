#!/usr/bin/env python
#   pipescaler/sorters/regex_sorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

import re
from typing import Any, Generator, List, Optional, Union

from pipescaler.core import Sorter


####################################### CLASSES ########################################
class RegexSorter(Sorter):

    # region Builtins

    def __init__(
        self,
        regex: str,
        downstream_stages_for_matched: Optional[Union[str, List[str]]] = None,
        downstream_stages_for_unmatched: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.regex = re.compile(regex)

        if isinstance(downstream_stages_for_matched, str):
            downstream_stages_for_matched = [downstream_stages_for_matched]
        self.downstream_stages_for_matched = downstream_stages_for_matched

        if isinstance(downstream_stages_for_unmatched, str):
            downstream_stages_for_unmatched = [downstream_stages_for_unmatched]
        self.downstream_stages_for_unmatched = downstream_stages_for_unmatched

        desc = f"{self.name} {self.__class__.__name__}"
        if self.downstream_stages_for_matched is not None:
            desc += f"\n ├─ MATCH"
            if len(self.downstream_stages_for_matched) >= 2:
                for stage in self.downstream_stages_for_matched[:-1]:
                    desc += f"\n │  ├─ {stage}"
            desc += f"\n │  └─ {self.downstream_stages_for_matched[-1]}"
        if self.downstream_stages_for_unmatched is not None:
            desc += f"\n └─ UNMATCH"
            if len(self.downstream_stages_for_unmatched) >= 2:
                for stage in self.downstream_stages_for_unmatched[:-1]:
                    desc += f"\n    ├─ {stage}"
            desc += f"\n    └─ {self.downstream_stages_for_unmatched[-1]}"
        self.desc = desc

    def __call__(self) -> Generator[str, str, None]:
        while True:
            image = yield  # type: ignore
            if self.pipeline.verbosity >= 2:
                print(f"{self} processing: {image.name}")
            if self.regex.match(image.name):
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: match {image.name}")
                if self.downstream_stages_for_matched is not None:
                    for pipe in self.downstream_stages_for_matched:
                        self.pipeline.stages[pipe].send(image)
            else:
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: unmatch {image.name}")
                if self.downstream_stages_for_unmatched is not None:
                    for pipe in self.downstream_stages_for_unmatched:
                        self.pipeline.stages[pipe].send(image)

    # endregion
