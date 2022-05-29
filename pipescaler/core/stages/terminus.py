#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for termini."""
from __future__ import annotations

from abc import ABC

from pipescaler.core.stage import Stage


class Terminus(Stage, ABC):
    """Abstract base class for termini."""

    def __call__(self, infile: str, outfile: str) -> None:
        """Terminates an image.

        Arguments:
            infile: Input file
            outfile: Output file
        """
        raise NotImplementedError()

    @property
    def inlets(self) -> list[str]:
        """Inlets that flow into stage."""
        return ["inlet"]

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of stage."""
        return []