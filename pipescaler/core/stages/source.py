#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sources."""
from __future__ import annotations

from abc import abstractmethod

from pipescaler.core.stage import Stage


class Source(Stage):
    """Abstract base class for sources."""

    def __iter__(self):
        """Yield next image."""
        raise NotImplementedError()

    @property
    def inlets(self) -> list[str]:
        """Inlets that flow into stage."""
        return []

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of stage."""
        return ["default"]

    @staticmethod
    @abstractmethod
    def sort(filename):
        """Sort outfiles to be yielded by source."""
        raise NotImplementedError()
