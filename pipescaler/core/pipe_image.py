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

from os.path import basename, splitext
from typing import Tuple

from PIL import Image

from pipescaler.common import validate_input_path


####################################### CLASSES ########################################
class PipeImage:

    # region Builtins

    def __init__(self, infile: str) -> None:
        self.full_path = validate_input_path(infile)
        self.filename = basename(self.full_path)
        self.name = splitext(basename(self.filename))[0]
        self.ext = splitext(basename(self.filename))[1].strip(".")

        image = Image.open(self.full_path)
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
            return self.full_path

    # endregion

    # region Methods

    def log(self, stage_name: str, outfile: str, suffixes=None):
        if suffixes is None:
            suffixes = []
        self.history.append((stage_name, suffixes, outfile))

    def show(self):
        self.image.show()

    # endregion
