#!/usr/bin/env python
#   pipescaler/core/sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from abc import ABC

from pipescaler.core.stage import Stage


class Sorter(Stage, ABC):

    # region Builtins

    def __call__(self, infile: str) -> str:
        raise NotImplementedError()

    # endregion

    # region Properties

    @property
    def inlets(self):
        return ["inlet"]

    # endregion
