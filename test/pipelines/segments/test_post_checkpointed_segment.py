#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PostCheckpointedSegment."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast
from unittest.mock import Mock

import pytest
from PIL import Image

from pipescaler.core.pipelines import PipeObject, Segment
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.pipelines import CheckpointManager
from pipescaler.pipelines.segments import PostCheckpointedSegment


def test_cached_outputs_preserve_internal_checkpoints(tmp_path: Path):
    """Reuse persisted outputs and retain nested checkpoints during resume cleanup.

    Arguments:
        tmp_path: temporary checkpoint directory
    """
    cp_manager = CheckpointManager(tmp_path)
    input_image = PipeImage(image=Image.new("RGB", (2, 2), "red"), name="source")

    def recolor(input_obj: PipeObject) -> tuple[PipeObject, ...]:
        """Produce blue pixels while retaining the input image as a parent.

        Arguments:
            input_obj: input image whose lineage is retained
        Returns:
            recolored output image within a tuple
        """
        assert isinstance(input_obj, PipeImage)
        return (PipeImage(image=Image.new("RGB", (2, 2), "blue"), parents=input_obj),)

    segment = Mock(wraps=recolor)
    inner = cp_manager.pre_segment("internal.png")(segment)
    wrapper = cp_manager.post_segment("post.png")(inner)
    initial_output = wrapper(input_image)[0]

    resumed_manager = CheckpointManager(tmp_path)
    resumed_segment = Mock(
        spec=Segment, side_effect=AssertionError("Cached segment runs again")
    )
    resumed_inner = resumed_manager.pre_segment("internal.png")(resumed_segment)
    resumed_wrapper = resumed_manager.post_segment("post.png")(resumed_inner)
    resumed_input = PipeImage(image=Image.new("RGB", (2, 2), "green"), name="source")
    cached_output = resumed_wrapper(resumed_input)[0]

    assert segment.call_count == 1
    assert cp_manager.observed_checkpoints == resumed_manager.observed_checkpoints
    assert resumed_manager.observed_checkpoints == {
        ("source", "internal.png"),
        ("source", "post.png"),
    }
    resumed_manager.purge_unrecognized_files()
    for output, parent in (
        (initial_output, input_image),
        (cached_output, resumed_input),
    ):
        assert isinstance(output, PipeImage)
        assert output.path == tmp_path / "source" / "post.png"
        assert output.parents == [parent]
        assert output.image.getpixel((0, 0)) == (0, 0, 255)
    with Image.open(tmp_path / "source" / "internal.png") as image:
        assert image.getpixel((0, 0)) == (255, 0, 0)


def test_non_callable_segment_validation(tmp_path: Path):
    """Reject a non-callable segment using a real checkpoint manager.

    Arguments:
        tmp_path: temporary checkpoint directory
    """
    cp_manager = CheckpointManager(tmp_path)
    with pytest.raises(
        ValueError, match="requires a callable Segment; int is not callable"
    ):
        PostCheckpointedSegment(cast(Any, 42), cp_manager, ["post.png"])


@pytest.mark.parametrize("output_count", [0, 2])
def test_rejects_wrong_output_count(tmp_path: Path, output_count: int):
    """Reject missing or extra outputs before publishing any checkpoint.

    Arguments:
        tmp_path: temporary checkpoint directory
        output_count: incorrect number of outputs for one checkpoint
    """
    cp_manager = CheckpointManager(tmp_path)
    input_image = PipeImage(image=Image.new("RGB", (1, 1)), name="source")

    def wrong_output_count(input_obj: PipeObject) -> tuple[PipeObject, ...]:
        """Return an incorrect number of outputs.

        Arguments:
            input_obj: image to repeat in the output tuple
        Returns:
            output objects with the requested incorrect count
        """
        return (input_obj,) * output_count

    wrapper = PostCheckpointedSegment(wrong_output_count, cp_manager, ["post.png"])
    with pytest.raises(
        ValueError, match=f"Expected 1 outputs .* but received {output_count}"
    ):
        wrapper(input_image)

    assert input_image.path is None
    assert not cp_manager.observed_checkpoints
    assert not any(tmp_path.iterdir())
