#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Pipe for AlphaSplitter."""
from __future__ import annotations

from typing import Type

from pipescaler.core.pipe import SplitterPipe
from pipescaler.core.stages import Splitter
from pipescaler.splitters import AlphaSplitter


class AlphaSplitterPipe(SplitterPipe):
    """Pipe for AlphaSplitter."""

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of pipe."""
        return ["color", "alpha"]

    @classmethod
    @property
    def splitter(cls) -> Type[Splitter]:
        """Type of splitter wrapped by pipe."""
        return AlphaSplitter
