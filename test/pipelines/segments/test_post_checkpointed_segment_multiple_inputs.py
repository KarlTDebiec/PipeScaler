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
    color_path = tmp_path / "color.png"
    alpha_path = tmp_path / "alpha.png"
    Image.new("RGB", (2, 2), "red").save(color_path)
    Image.new("L", (2, 2), 128).save(alpha_path)
    inputs = (
        PipeImage(path=color_path, name="color"),
        PipeImage(path=alpha_path, name=alpha_name),
    )
    checkpoint_dir_path = tmp_path / "checkpoints"
    cp_manager = CheckpointManager(checkpoint_dir_path)
    segment = Mock(wraps=ImageMergerSegment(AlphaMerger()))
    wrapper = cp_manager.post_segment("merged.png")(segment)

    initial_outputs = wrapper(*inputs)
    resumed_inputs = (
        PipeImage(path=color_path, name="color"),
        PipeImage(path=alpha_path, name=alpha_name),
    )
    resumed_manager = CheckpointManager(checkpoint_dir_path)
    resumed_segment = Mock(
        spec=ImageMergerSegment,
        side_effect=AssertionError("Cached segment runs again"),
    )
    resumed_wrapper = resumed_manager.post_segment("merged.png")(resumed_segment)
    cached_outputs = resumed_wrapper(*resumed_inputs)

    assert len(initial_outputs) == len(cached_outputs) == 1
    assert segment.call_count == 1
    resumed_segment.assert_not_called()
    assert cp_manager.observed_checkpoints == {("color", "merged.png")}
    assert resumed_manager.observed_checkpoints == cp_manager.observed_checkpoints
    resumed_manager.purge_unrecognized_files()
    for output, parents in zip(
        (*initial_outputs, *cached_outputs), (inputs, resumed_inputs)
    ):
        assert isinstance(output, PipeImage)
        assert output.path == checkpoint_dir_path / "color" / "merged.png"
        assert output.name == "color"
        assert output.parents == list(parents)
        assert (
            output.image.tobytes()
            == Image.new("RGBA", (2, 2), (255, 0, 0, 128)).tobytes()
        )
