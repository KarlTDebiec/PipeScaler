#!/usr/bin/env python
#   pipescaler/core/sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for sorters."""
from __future__ import annotations

from abc import ABC

from pipescaler.core.stage import Stage


class Sorter(Stage, ABC):
    """Base class for sorters."""

    def __call__(self, infile: str) -> str:
        """

        Args:
            infile:

        Returns:

        """
        raise NotImplementedError()

    @property
    def inlets(self):
        """Inlets that flow into stage"""
        return ["inlet"]
