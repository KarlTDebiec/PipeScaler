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
from IPython import embed
from PIL import Image

from lauhseuisin.sorters.Sorter import Sorter


################################### CLASSES ###################################
class TextImageSorter(Sorter):

    def __init__(self,
                 downstream_pipes_for_text: Optional[
                     Union[str, List[str]]] = None,
                 downstream_pipes_for_time_text: Optional[
                     Union[str, List[str]]] = None,
                 downstream_pipes_for_large_text: Optional[
                     Union[str, List[str]]] = None,
                 downstream_pipes_for_nontext: Optional[
                     Union[str, List[str]]] = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        if isinstance(downstream_pipes_for_text, str):
            downstream_pipes_for_text = [downstream_pipes_for_text]
        self.downstream_pipes_for_text = downstream_pipes_for_text

        if isinstance(downstream_pipes_for_time_text, str):
            downstream_pipes_for_time_text = [downstream_pipes_for_time_text]
        self.downstream_pipes_for_time_text = downstream_pipes_for_time_text

        if isinstance(downstream_pipes_for_large_text, str):
            downstream_pipes_for_large_text = [downstream_pipes_for_large_text]
        self.downstream_pipes_for_large_text = downstream_pipes_for_large_text

        if isinstance(downstream_pipes_for_nontext, str):
            downstream_pipes_for_nontext = [downstream_pipes_for_nontext]
        self.downstream_pipes_for_nontext = downstream_pipes_for_nontext

    def __call__(self) -> Iterator[str]:
        while True:
            infile = (yield)
            image_type = self.get_image_type(infile)
            if image_type == "text":
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: text {infile}")
                if self.downstream_pipes_for_text is not None:
                    for pipe in self.downstream_pipes_for_text:
                        self.pipeline.pipes[pipe].send(infile)
            elif image_type == "time_text":
                print(f"TIME TEXT: {infile}")
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: text {infile}")
                if self.downstream_pipes_for_time_text is not None:
                    for pipe in self.downstream_pipes_for_time_text:
                        self.pipeline.pipes[pipe].send(infile)
            elif image_type == "large_text":
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: text {infile}")
                if self.downstream_pipes_for_large_text is not None:
                    for pipe in self.downstream_pipes_for_large_text:
                        self.pipeline.pipes[pipe].send(infile)
            else:
                if self.pipeline.verbosity >= 2:
                    print(f"{self}: nontext {infile}")
                if self.downstream_pipes_for_nontext is not None:
                    for pipe in self.downstream_pipes_for_nontext:
                        self.pipeline.pipes[pipe].send(infile)

    def get_image_type(self, infile: str) -> str:
        data = np.array(Image.open(infile))

        if data.shape == (256, 256, 4):
            if data[:, :, :3].sum() == 0:
                return "text"
            y, x, _ = np.where(data == 255)
            if x.size > 0 and y.size > 0 and y.max() == 15 and x.max() < 128:
                return "time_text"
        elif data.shape == (32, 256, 4) or data.shape == (64, 256, 4):
            if (np.all(data[:, :, 0] == data[:, :, 1])
                    and np.all(data[:, :, 0] == data[:, :, 2])
                    and (data[:, :, 3] != 255).sum() != 0):
                return "large_text"

        return "nontext"
