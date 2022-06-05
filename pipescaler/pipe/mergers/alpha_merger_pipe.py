#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Pipe for AlphaMerger."""
from __future__ import annotations

from typing import Iterator, Type

from pipescaler.core import PipeImage
from pipescaler.core.pipe import MergerPipe
from pipescaler.core.stages import Merger
from pipescaler.mergers import AlphaMerger


class AlphaMergerPipe(MergerPipe):
    """Pipe for AlphaMerger."""

    def get_outlets(self, upstream_outlets):
        # TODO: Do some checks to make sure inlets and outlets align
        color_inlet, alpha_inlet = tuple(upstream_outlets.values())

        def outlet() -> Iterator[PipeImage]:
            for color_inlet_image, alpha_inlet_image in zip(color_inlet, alpha_inlet):
                outlet_image = self.merger_object(
                    color_inlet_image.image, alpha_inlet_image.image
                )
                yield PipeImage(outlet_image, [color_inlet_image, alpha_inlet_image])

        outlets = {"outlet": outlet()}
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
