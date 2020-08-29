#!/usr/bin/env python
#   pipescaler/core/pipe_image.py
#
#   Copyright (C) 2020 Karl T Debiec
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
        self._infile = validate_input_path(infile)
        image = Image.open(self.infile)
        self._mode: str = image.mode
        self._shape: Tuple[int] = image.size

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    # endregion

    # region Properties

    @property
    def ext(self) -> str:
        """str: Name"""
        return get_ext(self.infile)

    @property
    def infile(self) -> str:
        """str: Path to infile"""
        return self._infile

    @property
    def mode(self) -> str:
        """str: Image mode"""
        return self._mode

    @property
    def name(self) -> str:
        """str: Name"""
        return get_name(self.infile)

    @property
    def shape(self) -> Tuple[int]:
        """Tuple[int]: Image shape"""
        return self._shape

    # endregion
