#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for pipelines"""
from pytest import mark

from pipescaler.pipe.mergers import AlphaMergerPipe
from pipescaler.pipe.processors import XbrzProcessorPipe
from pipescaler.pipe.processors.xbrz_processor_pipe import processor_coroutine
from pipescaler.pipe.sources import DirectorySource
from pipescaler.pipe.splitters.alpha_splitter_pipe import AlphaSplitterPipe
from pipescaler.processors import XbrzProcessor
from pipescaler.testing import get_sub_directory


@mark.asyncio
async def test() -> None:
    directory_source = DirectorySource(get_sub_directory("basic"))
    alpha_merger = AlphaMergerPipe()
    alpha_splitter = AlphaSplitterPipe()
    xbrz_processor = XbrzProcessorPipe()

    # source.flow_into(alpha_splitter).flow_into(
    #     xbrz_processor.flow_into(xbrz_processor),
    #     xbrz_processor.flow_into(xbrz_processor),
    # ).flow_into(alpha_merger)
    xbrz_processor = processor_coroutine(XbrzProcessor())
    for outlets in directory_source:
        nay = await xbrz_processor(outlets)
        print(nay)
