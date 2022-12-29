#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for PreCheckpointedSegment."""
from __future__ import annotations

from unittest.mock import Mock

from pipescaler.common import PathLike, get_temp_directory_path, validate_output_file
from pipescaler.core.pipelines import PipeObject, Segment
from pipescaler.pipelines import CheckpointManager
from pipescaler.pipelines.segments import PreCheckpointedSegment


def mock_pipe_object_save(path: PathLike) -> None:
    """Save object to file and set path.

    Arguments:
        path: Path to which to save object
    """
    path = validate_output_file(path)
    path.touch()


def test():
    with get_temp_directory_path() as cp_directory:
        # Mocks
        mock_segment = Mock(spec=Segment)
        mock_cp_manager = Mock(spec=CheckpointManager)
        mock_cp_manager.directory = cp_directory
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
            cp_directory / mock_pipe_object.location_name / "pre.txt",
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

        # Test __str__ and __repr__
        print(pre_checkpointed_segment)
        print(repr(pre_checkpointed_segment))
