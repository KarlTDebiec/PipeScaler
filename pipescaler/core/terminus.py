#!/usr/bin/env python
#   pipescaler/core/processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from abc import abstractmethod
from typing import Any, List

from pipescaler.common import CLTool
from pipescaler.core.stage import Stage


####################################### CLASSES ########################################
class Terminus(Stage, CLTool):

    # region Builtins

    def __call__(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile)

    # endregion

    # region Properties

    @property
    def inlets(self) -> List[str]:
        return ["inlet"]

    @property
    def outlets(self) -> List[str]:
        return []

    # endregion

    # region Class Methods

    @classmethod
    @abstractmethod
    def process_file(cls, inlet: str, outfile: str, **kwargs: Any) -> None:
        raise NotImplementedError()

    # endregion
