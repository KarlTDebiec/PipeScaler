#!/usr/bin/env python
#   pipescaler/core/processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for termini."""
from __future__ import annotations

from abc import abstractmethod
from typing import List

from pipescaler.common import CLTool
from pipescaler.core.stage import Stage


class Terminus(Stage, CLTool):
    """Base class for termini."""

    def __call__(self, infile: str, outfile: str) -> None:
        """

        Args:
            infile:
            outfile:

        Returns:

        """
        self.process_file(infile, outfile)

    @property
    def inlets(self) -> List[str]:
        """Inlets that flow into stage"""
        return ["inlet"]

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return []

    @abstractmethod
    def process_file(cls, inlet: str, outfile: str) -> None:
        """

        Args:
            inlet:
            outfile:

        Returns:

        """
        raise NotImplementedError()
