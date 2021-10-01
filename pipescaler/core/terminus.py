#!/usr/bin/env python
#   pipescaler/core/processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from abc import abstractmethod
from typing import List

from pipescaler.common import CLTool
from pipescaler.core.stage import Stage


class Terminus(Stage, CLTool):
    def __call__(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile)

    @property
    def inlets(self) -> List[str]:
        return ["inlet"]

    @property
    def outlets(self) -> List[str]:
        return []

    @abstractmethod
    def process_file(cls, inlet: str, outfile: str) -> None:
        raise NotImplementedError()
