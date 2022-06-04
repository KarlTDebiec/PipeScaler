#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Pipe for AlphaMerger."""
from __future__ import annotations

from typing import Type

from pipescaler.core.pipe import MergerPipe
from pipescaler.core.stages import Merger
from pipescaler.mergers import AlphaMerger


class AlphaMergerPipe(MergerPipe):
    """Pipe for AlphaMerger."""

    @property
    def inlets(self) -> list[str]:
        """Inlets that flow into stage."""
        return ["color", "alpha"]

    @classmethod
    @property
    def merger(cls) -> Type[Merger]:
        """Type of merger wrapped by pipe."""
        return AlphaMerger
