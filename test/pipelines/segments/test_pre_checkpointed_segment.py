#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PreCheckpointedSegment."""

from __future__ import annotations

from os import utime
from pathlib import Path
from typing import Any, cast
from unittest.mock import Mock

import pytest
from PIL import Image

from pipescaler.core.pipelines import PipeObject, Segment
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.pipelines import CheckpointManager
from pipescaler.pipelines.segments import PreCheckpointedSegment


def test_inputs_are_saved_before_segment_execution(tmp_path: Path):
    """Persist input pixels before the wrapped segment runs and retain lineage.

    Arguments:
        tmp_path: temporary checkpoint directory
    """
    parent = PipeImage(image=Image.new("RGB", (2, 2), "red"), name="source")
    input_image = PipeImage(image=parent.image.copy(), parents=parent)
    cp_manager = CheckpointManager(tmp_path)
    checkpoint_path = tmp_path / "source" / "pre.png"

    def read_checkpoint(input_obj: PipeObject) -> tuple[PipeObject, ...]:
        """Read the persisted input while the wrapped segment is executing.

        Arguments:
            input_obj: checkpointed input image
        Returns:
            unchanged input image within a tuple
        """
        assert input_obj.path == checkpoint_path
        with Image.open(checkpoint_path) as image:
            assert image.getpixel((0, 0)) == (255, 0, 0)
        return (input_obj,)

    wrapper = PreCheckpointedSegment(read_checkpoint, cp_manager, ["pre.png"])

    assert wrapper(input_image) == (input_image,)
    assert input_image.parents == [parent]
    assert cp_manager.observed_checkpoints == {("source", "pre.png")}


def test_multiple_inputs_use_their_own_checkpoint_paths(tmp_path: Path):
    """Pair each input with its checkpoint without losing paths during cleanup.

    Arguments:
        tmp_path: temporary directory for checkpoints
    """
    inputs = (
        PipeImage(image=Image.new("RGB", (2, 2), "red"), name="first"),
        PipeImage(image=Image.new("RGB", (2, 2), "blue"), name="second"),
    )
    checkpoint_paths = (tmp_path / "first" / "a.png", tmp_path / "second" / "b.png")
    cp_manager = CheckpointManager(tmp_path)
    segment = Mock(spec=Segment, return_value=inputs)
    wrapper = cp_manager.pre_segment("a.png", "b.png")(segment)

    assert wrapper(*inputs) == inputs
    assert tuple(image.path for image in inputs) == checkpoint_paths
    assert cp_manager.observed_checkpoints == {("first", "a.png"), ("second", "b.png")}
    cp_manager.purge_unrecognized_files()
    for checkpoint_path, expected_color in zip(
        checkpoint_paths, ((255, 0, 0), (0, 0, 255))
    ):
        with Image.open(checkpoint_path) as image:
            assert image.getpixel((0, 0)) == expected_color

    wrapper(*inputs)
    assert tuple(image.path for image in inputs) == checkpoint_paths
    assert segment.call_count == 2


def test_non_callable_segment_validation(tmp_path: Path):
    """Reject a non-callable segment using a real checkpoint manager.

    Arguments:
        tmp_path: temporary checkpoint directory
    """
    cp_manager = CheckpointManager(tmp_path)
    with pytest.raises(
        ValueError, match="requires a callable Segment; str is not callable"
    ):
        PreCheckpointedSegment(cast(Any, "not_a_callable"), cp_manager, ["pre.png"])


def test_stale_multiple_inputs_keep_positional_checkpoint_mapping(tmp_path: Path):
    """Refresh stale checkpoints using each input's matching checkpoint name.

    Arguments:
        tmp_path: temporary directory for input and checkpoint files
    """
    source_paths = (tmp_path / "first.png", tmp_path / "second.png")
    for source_path, color in zip(source_paths, ("red", "green")):
        Image.new("RGB", (2, 2), color).save(source_path)
    cp_manager = CheckpointManager(tmp_path / "checkpoints", validate_input_mtime=True)

    def identity(*input_objs: PipeObject) -> tuple[PipeObject, ...]:
        """Return input objects unchanged.

        Arguments:
            *input_objs: images being checkpointed
        Returns:
            input objects within a tuple
        """
        return input_objs

    segment = Mock(wraps=identity)
    wrapper = cp_manager.pre_segment("first.png", "second.png")(segment)
    wrapper(
        PipeImage(path=source_paths[0], name="first"),
        PipeImage(path=source_paths[1], name="second"),
    )
    checkpoint_paths = (
        cp_manager.dir_path / "first" / "first.png",
        cp_manager.dir_path / "second" / "second.png",
    )
    for source_path, checkpoint_path, color in zip(
        source_paths, checkpoint_paths, ("blue", "yellow")
    ):
        Image.new("RGB", (2, 2), color).save(source_path)
        source_mtime_ns = checkpoint_path.stat().st_mtime_ns + 1_000_000_000
        utime(source_path, ns=(source_mtime_ns, source_mtime_ns))

    outputs = wrapper(
        PipeImage(path=source_paths[0], name="first"),
        PipeImage(path=source_paths[1], name="second"),
    )

    assert tuple(output.path for output in outputs) == checkpoint_paths
    for checkpoint_path, color in zip(checkpoint_paths, ("blue", "yellow")):
        with Image.open(checkpoint_path) as image:
            assert image.getpixel((0, 0)) == Image.new("RGB", (1, 1), color).getpixel(
                (0, 0)
            )


@pytest.mark.parametrize(
    ("validate_input_mtime", "stale", "expected_color"),
    (
        (True, True, (0, 0, 255)),
        (True, False, (255, 0, 0)),
        (False, True, (255, 0, 0)),
    ),
)
def test_checkpoint_freshness(
    tmp_path: Path,
    validate_input_mtime: bool,
    stale: bool,
    expected_color: tuple[int, int, int],
):
    """Reuse or rewrite pre-checkpoints according to configured freshness policy.

    Arguments:
        tmp_path: temporary directory for input and checkpoint files
        validate_input_mtime: whether checkpoint input mtimes are validated
        stale: whether the source mtime is newer than its checkpoint
        expected_color: pixel expected in the checkpoint
    """
    source_path = tmp_path / "source.png"
    Image.new("RGB", (2, 2), "red").save(source_path)
    cp_manager = CheckpointManager(
        tmp_path / "checkpoints", validate_input_mtime=validate_input_mtime
    )

    def identity(input_obj: PipeObject) -> tuple[PipeObject, ...]:
        """Return the input object.

        Arguments:
            input_obj: image being checkpointed
        Returns:
            input object within a tuple
        """
        return (input_obj,)

    segment = Mock(wraps=identity)
    wrapper = cp_manager.pre_segment("input.png")(segment)
    wrapper(PipeImage(path=source_path))
    checkpoint_path = cp_manager.dir_path / "source" / "input.png"
    Image.new("RGB", (2, 2), "blue").save(source_path)
    checkpoint_mtime_ns = checkpoint_path.stat().st_mtime_ns
    if stale:
        source_mtime_ns = checkpoint_mtime_ns + 1_000_000_000
    else:
        source_mtime_ns = max(1, checkpoint_mtime_ns - 1_000_000_000)
    utime(source_path, ns=(source_mtime_ns, source_mtime_ns))

    output = wrapper(PipeImage(path=source_path))[0]

    assert segment.call_count == 2
    assert output.path == checkpoint_path
    with Image.open(checkpoint_path) as image:
        assert image.getpixel((0, 0)) == expected_color


@pytest.mark.parametrize("input_count", [0, 2])
def test_rejects_wrong_input_count(tmp_path: Path, input_count: int):
    """Reject missing or extra inputs before saving files or running the segment.

    Arguments:
        tmp_path: temporary checkpoint directory
        input_count: incorrect number of inputs for one checkpoint
    """
    cp_manager = CheckpointManager(tmp_path)
    segment = Mock(
        spec=Segment, side_effect=AssertionError("Invalid inputs reached segment")
    )
    wrapper = PreCheckpointedSegment(segment, cp_manager, ["pre.png"])
    inputs = tuple(
        PipeImage(image=Image.new("RGB", (1, 1)), name=f"image{index}")
        for index in range(input_count)
    )

    with pytest.raises(
        ValueError, match=f"Expected 1 inputs .* but received {input_count}"
    ):
        wrapper(*inputs)

    assert not cp_manager.observed_checkpoints
    assert not any(tmp_path.iterdir())
