#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for pipelines"""
from pipescaler.pipe.mergers import AlphaMergerPipe
from pipescaler.pipe.processors import XbrzProcessorPipe
from pipescaler.pipe.sources import DirectorySource
from pipescaler.pipe.splitters.alpha_splitter_pipe import AlphaSplitterPipe
from pipescaler.testing import get_sub_directory


def test() -> None:
    source = DirectorySource(get_sub_directory("basic"))
    alpha_merger = AlphaMergerPipe()
    alpha_splitter = AlphaSplitterPipe()
    xbrz_processor = XbrzProcessorPipe()

    for outlets in source:
        print(outlets)
