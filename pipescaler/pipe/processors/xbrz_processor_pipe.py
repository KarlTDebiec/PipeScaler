#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Pipe for XbrzProcessor."""
from __future__ import annotations

from typing import Iterator, Type

from pipescaler.core import PipeImage
from pipescaler.core.pipe import ProcessorPipe
from pipescaler.core.stages import Processor
from pipescaler.processors.image import XbrzProcessor


class XbrzProcessorPipe(ProcessorPipe):
    """Pipe for XbrzProcessor."""

    def get_outlets(self, upstream_outlets) -> dict[str, Iterator[PipeImage]]:
        # TODO: Do some checks to make sure inlets and outlets align
        inlet = next(iter(upstream_outlets.values()))

        def outlet() -> Iterator[PipeImage]:
            for inlet_pipe_image in inlet:
                inlet_image = inlet_pipe_image.image
                outlet_image = self.processor_object(inlet_image)
                yield PipeImage(outlet_image, inlet_pipe_image)

        outlets = {"outlet": outlet()}
        return outlets

    @classmethod
    @property
    def processor(cls) -> Type[Processor]:
        """Type of processor wrapped by pipe."""
        return XbrzProcessor
