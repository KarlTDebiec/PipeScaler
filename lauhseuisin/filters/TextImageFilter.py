#!python
# -*- coding: utf-8 -*-
#   filters/TextImageFilter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

import re
from abc import ABC
from os.path import basename, dirname
from typing import Any, Generator, List, Optional

import numpy as np
from PIL import UnidentifiedImageError
from PIL import Image

from lauhseuisin.filters import Filter


################################### CLASSES ###################################
class TextImageFilter(Filter):

    def __call__(self,
                 downstream_pipes: Optional[
                     List[Generator[None, str, None]]] = None) \
            -> Generator[None, str, None]:
        while True:
            infile = (yield)
            if self.filter_file(infile):
                if downstream_pipes is not None:
                    for downstream_pipe in downstream_pipes:
                        downstream_pipe.send(infile)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return self.__repr__()

    def filter_file(self, infile: str) -> bool:
        try:
            image = Image.open(infile)
            data = np.array(image)
        except UnidentifiedImageError:
            return False

        if data[:, :, :3].sum() != 0:
            print(f"{self}{infile}")
            return True

        return False

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Filter]:
        return [cls(**kwargs)]
