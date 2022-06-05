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
    print()

    directory_source = DirectorySource(get_sub_directory("basic_temp"))
    xbrz_processor_pipe = XbrzProcessorPipe()
    alpha_splitter_pipe = AlphaSplitterPipe()
    alpha_merger_pipe = AlphaMergerPipe()

    source_outlets = directory_source.get_outlets()
    alpha_splitter_outlets = alpha_splitter_pipe.get_outlets(source_outlets)
    yat = xbrz_processor_pipe.get_outlets({"color": alpha_splitter_outlets["color"]})
    yat = xbrz_processor_pipe.get_outlets(yat)
    eee = xbrz_processor_pipe.get_outlets({"alpha": alpha_splitter_outlets["alpha"]})
    eee = xbrz_processor_pipe.get_outlets(eee)
    alpha_merger_outlets = alpha_merger_pipe.get_outlets(
        {
            "color": next(iter(yat.values())),
            "alpha": next(iter(eee.values())),
        }
    )
    print(alpha_merger_outlets)
    for image in alpha_merger_outlets["outlet"]:
        print(image)
