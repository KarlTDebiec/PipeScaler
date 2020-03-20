#!python
#   lauhseuisin/sorters/TransparencySorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from collections import Iterator
from typing import Any, List, Optional, Union

import numpy as np
from PIL import Image

from lauhseuisin.sorters.Sorter import Sorter


################################### CLASSES ###################################
class TransparencySorter(Sorter):

    def __init__(self,
                 downstream_pipes_for_transparent: Optional[
                     Union[str, List[str]]] = None,
                 downstream_pipes_for_opaque: Optional[
                     Union[str, List[str]]] = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        if isinstance(downstream_pipes_for_transparent, str):
            downstream_pipes_for_transparent = \
                [downstream_pipes_for_transparent]
        self.downstream_pipes_for_transparent = \
            downstream_pipes_for_transparent

        if isinstance(downstream_pipes_for_opaque, str):
            downstream_pipes_for_opaque = \
                [downstream_pipes_for_opaque]
        self.downstream_pipes_for_opaque = \
            downstream_pipes_for_opaque

    def __call__(self) -> Iterator[str]:
        while True:
            infile: str = (yield)
            if self.is_transparent(infile):
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: text {infile}")
                if self.downstream_pipes_for_transparent is not None:
                    for pipe in self.downstream_pipes_for_transparent:
                        self.pipeline.pipes[pipe].send(infile)
            else:
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: nontext {infile}")
                if self.downstream_pipes_for_opaque is not None:
                    for pipe in self.downstream_pipes_for_opaque:
                        self.pipeline.pipes[pipe].send(infile)

    def is_transparent(self, infile: str) -> bool:
        data = np.array(Image.open(infile))

        if data.shape[2] != 4:
            return False
        if (data[:, :, 3] != 255).sum() == 0:
            return False
        return True
