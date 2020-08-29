#!/usr/bin/env python
#   pipescaler/sorters/size_sorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import Any, Generator, List, Optional, Union

import numpy as np
from PIL import Image

from pipescaler.sorters.sorter import Sorter


####################################### CLASSES ########################################
class SizeSorter(Sorter):

    # region Builtins
    def __init__(
            self,
            cutoff: int = 16,
            downstream_pipes_for_small: Optional[Union[str, List[str]]] = None,
            downstream_pipes_for_large: Optional[Union[str, List[str]]] = None,
            **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.cutoff = cutoff
        self.desc = str(cutoff)

        if isinstance(downstream_pipes_for_small, str):
            downstream_pipes_for_small = [downstream_pipes_for_small]
        self.downstream_pipes_for_small = downstream_pipes_for_small

        if isinstance(downstream_pipes_for_large, str):
            downstream_pipes_for_large = [downstream_pipes_for_large]
        self.downstream_pipes_for_large = downstream_pipes_for_large

    def __call__(self) -> Generator[str, str, None]:
        while True:
            infile: str = yield  # type: ignore
            if self.is_small(infile):
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: small {infile}")
                if self.downstream_pipes_for_small is not None:
                    for pipe in self.downstream_pipes_for_small:
                        self.pipeline.pipes[pipe].send(infile)
            else:
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: large {infile}")
                if self.downstream_pipes_for_large is not None:
                    for pipe in self.downstream_pipes_for_large:
                        self.pipeline.pipes[pipe].send(infile)

    # endregion

    # region Methods

    def is_small(self, infile: str) -> bool:
        data = np.array(Image.open(infile))

        if min(data.shape[:2]) <= self.cutoff:
            return True
        else:
            return False

    # endregion
