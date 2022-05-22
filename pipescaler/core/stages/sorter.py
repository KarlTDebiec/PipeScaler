#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sorters."""
from __future__ import annotations

from abc import ABC

from pipescaler.core.stage import Stage


class Sorter(Stage, ABC):
    """Base class for sorters."""

    def __call__(self, infile: str) -> str:
        """Sort image into an outlet.

        Arguments:
            infile: Input file

        Returns:
            Outlet
        """
        raise NotImplementedError()

    @property
    def inlets(self) -> list[str]:
        """Inlets that flow into stage."""
        return ["inlet"]
