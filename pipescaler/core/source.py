#!/usr/bin/env python
#   pipescaler/core/source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from abc import abstractmethod

from pipescaler.core import Stage


class Source(Stage):

    # region Builtins

    def __iter__(self):
        raise NotImplementedError()

    # endregion

    # region Properties

    @property
    def inlets(self):
        return []

    @property
    def outlets(self):
        return ["default"]

    # endregion

    # region Static Methods

    @staticmethod
    @abstractmethod
    def sort(filename):
        raise NotImplementedError()

    # endregion
