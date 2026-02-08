#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PostCheckpointedSegment."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pipescaler.common.file import get_temp_directory_path
from pipescaler.common.validation import val_output_path
from pipescaler.core.pipelines import PipeObject, Segment
from pipescaler.pipelines import CheckpointManager
from pipescaler.pipelines.segments import PostCheckpointedSegment


def mock_pipe_object_save(path: Path | str):
    """Save object to file and set path.

    Arguments:
        path: Path to which to save object
    """
    path = val_output_path(path)
    path.touch()


def mock_pipe_object_save_2(self, path: Path | str):
    """Save object to file and set path.

    Arguments:
        self: not used; present for compatibility with PipeObject.save
        path: Path to which to save object
    """
    path = val_output_path(path)
    path.touch()


def test_non_callable_segment_validation():
    """Test that non-callable segment raises appropriate ValueError."""
    with get_temp_directory_path() as cp_directory_path:
        # Mocks
        non_callable_segment = 42  # Integer is not callable
        mock_cp_manager = Mock(spec=CheckpointManager)
        mock_cp_manager.directory = cp_directory_path

        # Attempt to initialize with non-callable segment
        with pytest.raises(ValueError) as exc_info:
            PostCheckpointedSegment(non_callable_segment, mock_cp_manager, ["test.txt"])

        # Verify the error message contains expected content
        error_message = str(exc_info.value)
        assert "requires a callable Segment" in error_message
        assert "int" in error_message  # The class name of the non-callable
        assert "is not callable" in error_message


@patch.object(PipeObject, "save", mock_pipe_object_save_2)
@patch.object(PipeObject, "__abstractmethods__", set())
def test():
    """Test PostCheckpointedSegment managing checkpoints after segment execution."""
    with get_temp_directory_path() as cp_directory_path:
        # Mocks
        mock_segment = Mock(spec=Segment)
        mock_cp_manager = Mock(spec=CheckpointManager)
        mock_cp_manager.directory = cp_directory_path
        mock_pipe_object_input = Mock(spec=PipeObject)
        mock_pipe_object_input.location_name = "test"
        mock_pipe_object_output = Mock(spec=PipeObject)
        mock_pipe_object_output.location_name = "test"
        mock_pipe_object_output.save.side_effect = mock_pipe_object_save

        # Initialize
        post_checkpointed_segment = PostCheckpointedSegment(
            mock_segment, mock_cp_manager, ["post.txt"], internal_cpts=["internal.txt"]
        )

        # Too many outputs
        mock_segment.return_value = (Mock(), Mock())
        try:
            post_checkpointed_segment(mock_pipe_object_input)
        except ValueError:
            pass

        # New checkpoint
        mock_segment.return_value = (mock_pipe_object_output,)
        post_checkpointed_segment(mock_pipe_object_input)
        assert mock_pipe_object_input.save.call_count == 0
        assert mock_pipe_object_output.save.call_count == 1
        assert mock_pipe_object_output.save.call_args_list[0][0] == (
            cp_directory_path / mock_pipe_object_input.location_name / "post.txt",
        )
        assert mock_cp_manager.observe.call_count == 1
        assert mock_cp_manager.observe.call_args_list[0][0] == (
            mock_pipe_object_input.location_name,
            "post.txt",
        )

        # Existing checkpoint
        post_checkpointed_segment(mock_pipe_object_input)
        assert mock_pipe_object_input.save.call_count == 0
        assert mock_pipe_object_output.save.call_count == 1
        assert mock_cp_manager.observe.call_count == 3
        assert mock_cp_manager.observe.call_args_list[1][0] == (
            mock_pipe_object_input.location_name,
            "internal.txt",
        )
        assert mock_cp_manager.observe.call_args_list[2][0] == (
            mock_pipe_object_input.location_name,
            "post.txt",
        )

        # Test miscellaneous methods
        print(post_checkpointed_segment)
        print(repr(post_checkpointed_segment))
