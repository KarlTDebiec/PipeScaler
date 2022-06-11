#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for pipelines."""
from typing import Iterator

from pipescaler.core import PipeImage
from pipescaler.core.pipelines import route
from pipescaler.core.pipelines.functions import wrap_sorter
from pipescaler.image.mergers import AlphaMerger
from pipescaler.image.splitters import AlphaSplitter
from pipescaler.pipelines.checkpoint_manager import CheckpointManager
from pipescaler.pipelines.sorters import AlphaSorter
from pipescaler.pipelines.sources import DirectorySource
from pipescaler.pipelines.termini import CopyFileTerminus
from pipescaler.processors import XbrzProcessor
from pipescaler.testing import get_sub_directory


def test() -> None:
    print()
    source = DirectorySource(get_sub_directory("basic"))
    checkpoints = CheckpointManager(r"C:\Users\karls\OneDrive\Desktop\wip")
    xbrz = XbrzProcessor()
    alpha_sorter = AlphaSorter()
    splitter = AlphaSplitter()
    merger = AlphaMerger()
    terminus = CopyFileTerminus(r"C:\Users\karls\OneDrive\Desktop\output")

    def block_rgb(inlet: Iterator[PipeImage]) -> Iterator[PipeImage]:
        with checkpoints.cp("color", inlet) as color_cp:
            color = route(xbrz, color_cp.to_do)
            color = route(xbrz, color)
            color = color_cp.save(color)
        return color

    def block_a(inlet: Iterator[PipeImage]) -> Iterator[PipeImage]:
        with checkpoints.cp("alpha", inlet) as alpha_cp:
            alpha = route(xbrz, alpha_cp.to_do)
            alpha = route(xbrz, alpha)
            alpha = alpha_cp.save(alpha)
        return alpha

    def block_rgba(inlet: Iterator[PipeImage]) -> Iterator[PipeImage]:
        with checkpoints.cp("merged", inlet) as merged_cp:
            color, alpha = route(splitter, merged_cp.to_do)
            color = block_rgb(color)
            alpha = block_a(alpha)
            merged = route(merger, [color, alpha])
            merged = merged_cp.save(merged)
        return merged

    with checkpoints.cp("original", source) as original_cp:
        source = original_cp.save(original_cp.to_do)
    drop_alpha, keep_alpha, no_alpha = wrap_sorter(alpha_sorter, source)
    keep_alpha = block_rgba(keep_alpha)
    no_alpha = block_rgb(no_alpha)
    terminus(keep_alpha)
    terminus(no_alpha)

    # checkpoints.purge_unrecognized_files()
    terminus.purge_unrecognized_files()

    for filepath in terminus.directory.iterdir():
        print(filepath)
        # Image.open(filepath).show()
