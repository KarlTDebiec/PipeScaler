#!/usr/bin/env python
#   pipescaler/core/splitter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pipescaler.core.stage import Stage


####################################### CLASSES ########################################
class Splitter(Stage, ABC):

    # region Properties

    @property
    def inlets(self):
        return ["default"]

    # endregion

    # region Class Methods

    @classmethod
    @abstractmethod
    def process_file(cls, infile: str, verbosity: int = 1, **kwargs: Any) -> None:
        raise NotImplementedError()

    # endregion
