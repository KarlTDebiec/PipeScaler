#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for pipelines."""
from tempfile import TemporaryDirectory

from PIL import Image

from pipescaler.core.pipe import route
from pipescaler.mergers import AlphaMerger
from pipescaler.pipe.sources import DirectorySource
from pipescaler.pipe.termini import CopyFileTerminus
from pipescaler.processors import XbrzProcessor
from pipescaler.splitters import AlphaSplitter
from pipescaler.testing import get_sub_directory


def test() -> None:
    print()

    with TemporaryDirectory() as output_directory:
        directory_source = DirectorySource(get_sub_directory("basic_temp"))
        xbrz_processor = XbrzProcessor()
        alpha_splitter = AlphaSplitter()
        alpha_merger = AlphaMerger()
        copy_file_terminus = CopyFileTerminus(directory=output_directory)

        color_outlet, alpha_outlet = route(alpha_splitter, directory_source)
        color_outlet = route(xbrz_processor, route(xbrz_processor, color_outlet))
        alpha_outlet = route(xbrz_processor, route(xbrz_processor, alpha_outlet))

        alpha_merger_outlet = route(alpha_merger, [color_outlet, alpha_outlet])
        copy_file_terminus(alpha_merger_outlet)
        copy_file_terminus.purge_unrecognized_files()
        for filepath in copy_file_terminus.directory.iterdir():
            print(filepath)
            Image.open(filepath).show()
