#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaMergerPipe."""
from __future__ import annotations

from PIL import Image
from pytest import mark

from pipescaler.core import PipeImage
from pipescaler.core.pipe.pipe import Pipe
from pipescaler.pipe.mergers.alpha_merger_pipe import AlphaMergerPipe
from pipescaler.pipe.processors import XbrzProcessorPipe
from pipescaler.pipe.splitters.alpha_splitter_pipe import AlphaSplitterPipe
from pipescaler.testing import get_infile


@mark.parametrize(
    ("pipe", "infiles"),
    [
        (AlphaMergerPipe(), ("split/RGBA_color_RGB", "split/RGBA_alpha_L")),
        (AlphaSplitterPipe(), ("RGBA",)),
        (XbrzProcessorPipe(), ("RGB",)),
    ],
)
def test(pipe: Pipe, infiles: tuple[str]) -> None:
    inlets = {
        pipe.inlets[i]: PipeImage(Image.open(get_infile(infile)))
        for i, infile in enumerate(infiles)
    }
    assert list(inlets.keys()) == pipe.inlets

    outlets = pipe(inlets)
    assert list(outlets.keys()) == pipe.outlets
    for outlet in outlets:
        assert outlets[outlet].parent == list(inlets.values())
