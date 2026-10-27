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

from pipescaler.common.file import get_temp_directory_path
from pipescaler.common.validation import val_output_path
from pipescaler.core.pipelines import PipeObject, Segment
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.pipelines import CheckpointManager
from pipescaler.pipelines.segments import PreCheckpointedSegment


def mock_pipe_object_save(path: Path | str):
    """Save object to file and set path.

    Arguments:
        path: Path to which to save object
    """
    path = val_output_path(path)
    path.touch()


def test_non_callable_segment_validation():
    """Test that non-callable segment raises appropriate ValueError."""
    with get_temp_directory_path() as cp_directory_path:
        # Mocks
        non_callable_segment = "not_a_callable"  # String is not callable
        mock_cp_manager = Mock(spec=CheckpointManager)
        mock_cp_manager.directory = cp_directory_path

        # Attempt to initialize with non-callable segment
        with pytest.raises(ValueError) as exc_info:
            PreCheckpointedSegment(
                cast(Any, non_callable_segment), mock_cp_manager, ["test.txt"]
            )

        # Verify the error message contains expected content
        error_message = str(exc_info.value)
        assert "requires a callable Segment" in error_message
        assert "str" in error_message  # The class name of the non-callable
        assert "is not callable" in error_message


def test():
    """Test PreCheckpointedSegment managing checkpoints before segment execution."""
    with get_temp_directory_path() as cp_dir_path:
        # Mocks
        mock_segment = Mock(spec=Segment)
        mock_cp_manager = Mock(spec=CheckpointManager)
        mock_cp_manager.dir_path = cp_dir_path
        mock_pipe_object = Mock(spec=PipeObject)
        mock_pipe_object.location_name = "test"
        mock_pipe_object.save.side_effect = mock_pipe_object_save

        # Initialize
        pre_checkpointed_segment = PreCheckpointedSegment(
            mock_segment, mock_cp_manager, ["pre.txt"]
        )

        # New checkpoint
        pre_checkpointed_segment(mock_pipe_object)
        assert mock_pipe_object.save.call_count == 1
        assert mock_pipe_object.save.call_args_list[0][0] == (
            cp_dir_path / mock_pipe_object.location_name / "pre.txt",
        )

        assert mock_cp_manager.observe.call_count == 1
        assert mock_cp_manager.observe.call_args_list[0][0] == (
            mock_pipe_object.location_name,
            "pre.txt",
        )

        # Existing checkpoint
        pre_checkpointed_segment(mock_pipe_object)
        assert mock_pipe_object.save.call_count == 1
        assert mock_cp_manager.observe.call_count == 2

        # Incorrect number of inputs
        try:
            pre_checkpointed_segment(Mock(), Mock())
        except ValueError:
            pass

        # Test miscellaneous methods
        assert str(pre_checkpointed_segment)
        assert repr(pre_checkpointed_segment)


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
