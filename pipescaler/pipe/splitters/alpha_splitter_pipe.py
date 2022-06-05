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

    def get_outlets(self, upstream_outlets):
        # TODO: Do some checks to make sure inlets and outlets align
        inlet = next(iter(upstream_outlets.values()))

        def outlet() -> Iterator[PipeImage]:
            for inlet_pipe_image in inlet:
                inlet_image = inlet_pipe_image.image
                outlet_images = self.splitter_object(inlet_image)
                yield {
                    outlet: PipeImage(outlet_images[i], inlet_pipe_image)
                    for i, outlet in enumerate(self.outlets)
                }

        color_outlet, alpha_outlet = tee(outlet())
        color_outlet = (elem["color"] for elem in color_outlet)
        alpha_outlet = (elem["alpha"] for elem in alpha_outlet)
        outlets = {"color": color_outlet, "alpha": alpha_outlet}
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
