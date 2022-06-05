#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sources."""
from abc import ABC


class Source(ABC):
    """Abstract base class for sources."""

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of source."""
        return ["outlet"]
