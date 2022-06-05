#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Pipe for AlphaSplitter."""
from __future__ import annotations

from itertools import tee
from typing import Iterator, Type

from pipescaler.core import PipeImage
from pipescaler.core.pipe import SplitterPipe
from pipescaler.core.stages import Splitter
from pipescaler.splitters import AlphaSplitter


class AlphaSplitterPipe(SplitterPipe):
    """Pipe for AlphaSplitter."""

    def route(
        self, inlets: dict[str, Iterator[PipeImage]]
    ) -> dict[str, Iterator[PipeImage]]:
        def outlet() -> Iterator[PipeImage]:
            for input_pipe_images in zip(*inlets.values()):
                input_images = (image.image for image in input_pipe_images)
                outlet_images = self.splitter_object(*input_images)
                yield {
                    outlet: PipeImage(outlet_images[i], input_pipe_images)
                    for i, outlet in enumerate(self.outlets)
                }

        if len(self.outlets) > 1:
            outlets = tee(outlet(), len(self.outlets))
            outlets = {
                outlet: (elem[outlet] for elem in outlets[i])
                for i, outlet in enumerate(self.outlets)
            }
        else:
            outlets = {self.outlets[0]: outlet()}
        return outlets

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of pipe."""
        return ["color", "alpha"]

    @classmethod
    @property
    def splitter(cls) -> Type[Splitter]:
        """Type of splitter wrapped by pipe."""
        return AlphaSplitter
