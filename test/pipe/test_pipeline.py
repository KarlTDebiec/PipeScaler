#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for pipelines."""
from tempfile import TemporaryDirectory

from PIL import Image

from pipescaler.core.pipe import route
from pipescaler.core.pipe.routing import sort
from pipescaler.mergers import AlphaMerger
from pipescaler.pipe.checkpoint_manager import CheckpointManager
from pipescaler.pipe.sorters import AlphaSorter
from pipescaler.pipe.sources import DirectorySource
from pipescaler.pipe.termini import CopyFileTerminus
from pipescaler.processors import XbrzProcessor
from pipescaler.splitters import AlphaSplitter
from pipescaler.testing import get_sub_directory


def test() -> None:
    print()

    with TemporaryDirectory() as output_directory, TemporaryDirectory() as checkpoint_directory:
        source = DirectorySource(get_sub_directory("basic"))
        checkpoints = CheckpointManager(r"C:\Users\karls\OneDrive\Desktop\test")
        xbrz = XbrzProcessor()
        alpha_sorter = AlphaSorter()
        splitter = AlphaSplitter()
        merger = AlphaMerger()
        terminus = CopyFileTerminus(directory=output_directory)

        with checkpoints.cp("original", source) as original_cp:
            source = original_cp.save(original_cp.to_do)
        drop_alpha, keep_alpha, no_alpha = sort(alpha_sorter, source)
        with checkpoints.cp("merged", keep_alpha) as merged_cp:
            color, alpha = route(splitter, merged_cp.to_do)
            with checkpoints.cp("color", color) as color_cp:
                color = route(xbrz, color_cp.to_do)
                color = route(xbrz, color)
                color = color_cp.save(color)
            with checkpoints.cp("alpha", alpha) as alpha_cp:
                alpha = route(xbrz, alpha_cp.to_do)
                alpha = route(xbrz, alpha)
                alpha = alpha_cp.save(alpha)
            merged = route(merger, [color, alpha])
            merged = merged_cp.save(merged)
        terminus(merged)
        checkpoints.purge_unrecognized_files()
        terminus.purge_unrecognized_files()

        for filepath in terminus.directory.iterdir():
            print(filepath)
            Image.open(filepath).show()
