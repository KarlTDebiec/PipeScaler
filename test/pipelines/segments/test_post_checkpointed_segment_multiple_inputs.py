#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for multiple-input post-checkpoint mapping."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest
from PIL import Image

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.operators.mergers import AlphaMerger
from pipescaler.image.pipelines.segments import ImageMergerSegment
from pipescaler.pipelines import CheckpointManager


@pytest.mark.parametrize("alpha_name", ["color", "alpha"])
def test_multiple_input_merger_cache_matches_initial_output(
    tmp_path: Path, alpha_name: str
):
    """Preserve merger output count, pixels, paths, and lineage across resume.

    Arguments:
        tmp_path: temporary directory for checkpoints
        alpha_name: name of the alpha input, shared with or distinct from color
    """
    inputs = (
        PipeImage(image=Image.new("RGB", (2, 2), "red"), name="color"),
        PipeImage(image=Image.new("L", (2, 2), 128), name=alpha_name),
    )
    cp_manager = CheckpointManager(tmp_path)
    segment = Mock(wraps=ImageMergerSegment(AlphaMerger()))
    wrapper = cp_manager.post_segment("merged.png")(segment)

    initial_outputs = wrapper(*inputs)
    cached_outputs = wrapper(*inputs)

    assert len(initial_outputs) == len(cached_outputs) == 1
    assert segment.call_count == 1
    assert cp_manager.observed_checkpoints == {("color", "merged.png")}
    cp_manager.purge_unrecognized_files()
    for output in (*initial_outputs, *cached_outputs):
        assert isinstance(output, PipeImage)
        assert output.path == tmp_path / "color" / "merged.png"
        assert output.name == "color"
        assert output.parents == list(inputs)
        assert output.image.getpixel((0, 0)) == (255, 0, 0, 128)
