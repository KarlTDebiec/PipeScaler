#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Pipe for AlphaMerger."""
from __future__ import annotations

from itertools import tee
from typing import Iterator, Type

from pipescaler.core import PipeImage
from pipescaler.core.pipe import MergerPipe
from pipescaler.core.stages import Merger
from pipescaler.mergers import AlphaMerger


class AlphaMergerPipe(MergerPipe):
    """Pipe for AlphaMerger."""

    def route(
        self, inlets: dict[str, Iterator[PipeImage]]
    ) -> dict[str, Iterator[PipeImage]]:
        def outlet() -> Iterator[PipeImage]:
            for input_pipe_images in zip(*inlets.values()):
                input_images = (image.image for image in input_pipe_images)
                output_image = self.merger_object(*input_images)
                output_pipe_image = PipeImage(output_image, input_pipe_images)
                yield output_pipe_image

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
    def inlets(self) -> list[str]:
        """Inlets that flow into pipe."""
        return ["color", "alpha"]

    @classmethod
    @property
    def merger(cls) -> Type[Merger]:
        """Type of merger wrapped by pipe."""
        return AlphaMerger
