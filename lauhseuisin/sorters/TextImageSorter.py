#!python
#   lauhseuisin/sorters/TextImageSorter.py
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
class TextImageSorter(Sorter):

    def __init__(self,
                 downstream_pipes_for_text: Optional[
                     Union[str, List[str]]] = None,
                 downstream_pipes_for_nontext: Optional[
                     Union[str, List[str]]] = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        if isinstance(downstream_pipes_for_text, str):
            downstream_pipes_for_text = [downstream_pipes_for_text]
        self.downstream_pipes_for_text = downstream_pipes_for_text

        if isinstance(downstream_pipes_for_nontext, str):
            downstream_pipes_for_nontext = [downstream_pipes_for_nontext]
        self.downstream_pipes_for_nontext = downstream_pipes_for_nontext

    def __call__(self) -> Iterator[str]:
        while True:
            infile = (yield)
            if self.is_text_image(infile):
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: text {infile}")
                if self.downstream_pipes_for_text is not None:
                    for pipe in self.downstream_pipes_for_text:
                        self.pipeline.pipes[pipe].send(infile)
            else:
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: nontext {infile}")
                if self.downstream_pipes_for_nontext is not None:
                    for pipe in self.downstream_pipes_for_nontext:
                        self.pipeline.pipes[pipe].send(infile)

    def is_text_image(self, infile: str) -> bool:
        data = np.array(Image.open(infile))

        if data.shape != (256, 256, 4):
            return False
        if data[:, :, :3].sum() != 0:
            return False
        return True
