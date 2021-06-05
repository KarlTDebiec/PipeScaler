#!/usr/bin/env python
#   pipescaler/core/source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from pipescaler.core import Stage


####################################### CLASSES ########################################
class Source(Stage):

    # region Builtins

    def __init__(self, **kwargs: Any,) -> None:
        super().__init__(**kwargs)

    def __iter__(self):
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.desc

    def __str__(self) -> str:
        return self.name

    # endregion

    # region Static Methods

    @staticmethod
    @abstractmethod
    def sort(filename):
        raise NotImplementedError()

    # endregion
