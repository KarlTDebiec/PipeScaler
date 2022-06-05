#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes for and functions related to pipes."""
from __future__ import annotations

from pipescaler.core.pipe.routing import route
from pipescaler.core.pipe.source import Source

__all__: list[str] = [
    "route",
    "Source",
]
