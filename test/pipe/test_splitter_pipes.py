#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaSplitterPipe."""
from __future__ import annotations

from PIL import Image
from pytest import mark

from pipescaler.core import PipeImage
from pipescaler.core.pipe import SplitterPipe
from pipescaler.pipe.splitters.alpha_splitter_pipe import AlphaSplitterPipe
from pipescaler.testing import get_infile


@mark.parametrize(
    ("pipe", "infile"),
    [
        (AlphaSplitterPipe(), "RGBA"),
    ],
)
def test(pipe: SplitterPipe, infile: str) -> None:
    inlet = PipeImage(Image.open(get_infile(infile)))
    inlets = {"inlet": inlet}
    assert list(inlets.keys()) == pipe.inlets

    outlets = pipe(inlets)
    assert list(outlets.keys()) == pipe.outlets
    for outlet in outlets:
        assert outlets[outlet].parent == inlet
