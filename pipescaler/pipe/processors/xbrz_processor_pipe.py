#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Pipe for XbrzProcessor."""
from __future__ import annotations

from typing import Type

from pipescaler.core.pipe import ProcessorPipe
from pipescaler.core.stages import Processor
from pipescaler.processors.image import XbrzProcessor


class XbrzProcessorPipe(ProcessorPipe):
    """Pipe for XbrzProcessor."""

    async def coroutine(self):
        while True:
            inlets = yield
            outlets = self(inlets)
            print(outlets)

    @classmethod
    @property
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by pipe."""
        return XbrzProcessor


async def processor_coroutine(processor, downstream_pipe=None):
    while True:
        inlets = yield
        outlets = processor(inlets)
        downstream_pipe.send(outlets)
