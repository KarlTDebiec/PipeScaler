#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for ProcessorPipes."""
from __future__ import annotations

from PIL import Image
from pytest import mark

from pipescaler.core import PipeImage
from pipescaler.core.pipe import ProcessorPipe
from pipescaler.pipe.processors.xbrz_processor_pipe import XbrzProcessorPipe
from pipescaler.testing import get_infile


@mark.parametrize(
    ("pipe", "infile"),
    [
        (XbrzProcessorPipe(), "RGB"),
    ],
)
def test(pipe: ProcessorPipe, infile: str) -> None:
    inlet = PipeImage(Image.open(get_infile(infile)))
    inlets = {"inlet": inlet}
    assert list(inlets.keys()) == pipe.inlets

    outlets = pipe(inlets)
    assert list(outlets.keys()) == pipe.outlets
    outlet = outlets["outlet"]
    assert outlet.parent == inlet
