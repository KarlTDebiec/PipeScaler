#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes for and functions related to pipes."""
from __future__ import annotations

from pipescaler.core.pipe.file_processor import FileProcessor
from pipescaler.core.pipe.routing import wrap_merger, wrap_processor, wrap_splitter
from pipescaler.core.pipe.source import Source
from pipescaler.core.pipe.terminus import Terminus

__all__: list[str] = [
    "FileProcessor",
    "Source",
    "Terminus",
    "wrap_merger",
    "wrap_processor",
    "wrap_splitter",
]
