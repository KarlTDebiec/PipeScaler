#!/usr/bin/env python
#   pipescaler/core/pipe_image.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import Tuple

from PIL import Image

from pipescaler.common import get_ext, get_name, validate_input_path


####################################### CLASSES ########################################
class PipeImage:

    # region Builtins

    def __init__(self, infile: str) -> None:
        self.infile = validate_input_path(infile)
        self.name = get_name(self.infile)
        self.ext = get_ext(self.infile)

        image = Image.open(self.infile)
        self.mode: str = image.mode
        self.shape: Tuple[int] = image.size

        self.history = []

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    # endregion

    # region Properties

    @property
    def image(self) -> Image:
        return Image.open(self.last)

    @property
    def last(self) -> str:
        if len(self.history) >= 1:
            return self.history[-1][1]
        else:
            return self.infile

    # endregion

    # region Methods

    def log(self, stage_name: str, outfile: str):
        self.history.append((stage_name, outfile))

    def show(self):
        self.image.show()

    # endregion
