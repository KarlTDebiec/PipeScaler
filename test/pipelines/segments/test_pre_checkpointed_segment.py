#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PreCheckpointedSegment."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from pipescaler.common.file import get_temp_directory_path
from pipescaler.common.validation import val_output_path
from pipescaler.core.pipelines import PipeObject, Segment
from pipescaler.pipelines import CheckpointManager
from pipescaler.pipelines.segments import PreCheckpointedSegment

if TYPE_CHECKING:
    from pathlib import Path


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
            PreCheckpointedSegment(non_callable_segment, mock_cp_manager, ["test.txt"])

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
        print(pre_checkpointed_segment)
        print(repr(pre_checkpointed_segment))
