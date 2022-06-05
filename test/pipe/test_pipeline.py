#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for pipelines"""
from pipescaler.core.pipe import route
from pipescaler.mergers import AlphaMerger
from pipescaler.pipe.sources import DirectorySource
from pipescaler.processors import XbrzProcessor
from pipescaler.splitters import AlphaSplitter
from pipescaler.testing import get_sub_directory


def test() -> None:
    print()

    directory_source = DirectorySource(get_sub_directory("basic_temp"))

    xbrz_processor = XbrzProcessor()
    alpha_splitter = AlphaSplitter()
    alpha_merger = AlphaMerger()

    source_outlets = directory_source.get_outlets()
    alpha_splitter_outlets = route(alpha_splitter, source_outlets)
    color_outlets = route(xbrz_processor, {"color": alpha_splitter_outlets["color"]})
    alpha_outlets = route(xbrz_processor, {"alpha": alpha_splitter_outlets["alpha"]})

    alpha_merger_outlets = route(
        alpha_merger,
        {
            "color": color_outlets["outlet"],
            "alpha": alpha_outlets["outlet"],
        },
    )
    for image in alpha_merger_outlets["outlet"]:
        print(image)
        image.image.show()
