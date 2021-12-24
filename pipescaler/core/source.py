#!/usr/bin/env python
#   pipescaler/core/source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for sources"""
from __future__ import annotations

from abc import abstractmethod
from typing import List

from pipescaler.core.stage import Stage


class Source(Stage):
    """Base class for sources"""

    def __iter__(self):
        """Yield next image from source"""
        raise NotImplementedError()

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return []

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["default"]

    @staticmethod
    @abstractmethod
    def sort(filename):
        """Sorts outfiles of source"""
        raise NotImplementedError()
