#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CheckpointManager."""

from __future__ import annotations

from platform import system
from unittest.mock import Mock, patch

from pipescaler.common.file import get_temp_directory_path
from pipescaler.common.validation import val_output_path
from pipescaler.core.pipelines import PipeObject, Segment
from pipescaler.pipelines import CheckpointManager

if system() == "Windows":
    from pathlib import Path, WindowsPath  # noqa: F401
    from pathlib import WindowsPath as PlatformPath

else:
    from pathlib import Path, PosixPath  # noqa: F401
    from pathlib import PosixPath as PlatformPath


def mock_pipe_object_save(path: Path | str):
    """Save object to file and set path.

    Arguments:
        path: Path to which to save object
    """
    path = val_output_path(path)
    path.touch()


def mock_pipe_object_save_2(self: PipeObject, path: Path | str):
    """Save object to file and set path.

    Arguments:
        self: PipeObject to which this mock method is attached
        path: Path to which to save object
    """
    path = val_output_path(path)
    path.touch()


@patch.object(PipeObject, "save", mock_pipe_object_save_2)
@patch.object(PipeObject, "__abstractmethods__", set())
def test_load_save():
    """Test CheckpointManager loading and saving checkpoints."""
    with get_temp_directory_path() as cp_dir_path:
        cp_manager = CheckpointManager(cp_dir_path)

        # Mocks
        mock_pipe_object_input = Mock(spec=PipeObject)
        mock_pipe_object_input.location_name = "test"
        mock_pipe_object_input.save.side_effect = mock_pipe_object_save

        # Attempt to load single unavailable checkpoint
        outputs = cp_manager.load((mock_pipe_object_input,), ("cpt.txt",))
        assert outputs is None

        # Attempt to load multiple unavailable checkpoints
        outputs = cp_manager.load((mock_pipe_object_input,), ("cpt.txt", "cpt2.txt"))
        assert outputs is None

        # Attempt to load invalid number of checkpoints
        mock_pipe_object_input_2 = Mock(spec=PipeObject)
        mock_pipe_object_input_2.location_name = "test2"
        try:
            cp_manager.load(
                (mock_pipe_object_input, mock_pipe_object_input_2), ("cpt.txt",)
            )
        except ValueError:
            pass

        # Attempt to save invalid number of checkpoints
        try:
            cp_manager.save((mock_pipe_object_input,), ("cpt.txt", "cpt2.txt"))
        except ValueError:
            pass

        # Save checkpoint
        cp_manager.save((mock_pipe_object_input,), ("cpt.txt",))
        assert (cp_dir_path / "test" / "cpt.txt").exists()

        # Try to save again, without overwriting
        outputs = cp_manager.save(
            (mock_pipe_object_input,), ("cpt.txt",), overwrite=False
        )
        assert outputs[0].path == (cp_dir_path / "test" / "cpt.txt")

        # Load checkpoint
        internal_segment = Mock(spec=Segment)
        internal_segment.cpts = ("cpt4.txt",)
        internal_segment.internal_cpts = ("cpt5.txt",)
        outputs = cp_manager.load(
            (mock_pipe_object_input,),
            ("cpt.txt",),
            calls=(
                "cpt3.txt",
                internal_segment,
            ),
        )
        assert outputs

        # Purge
        (cp_dir_path / "delete_me.txt").touch()
        (cp_dir_path / "delete_me").mkdir()
        (cp_dir_path / "delete_me" / "delete_me.txt").touch()
        cp_manager.purge_unrecognized_files()


def test_pre_segment():
    """Test CheckpointManager wrapping segments with pre-checkpointing."""
    with get_temp_directory_path() as cp_dir_path:
        cp_manager = CheckpointManager(cp_dir_path)
        cp_manager.pre_segment("cpt.txt")(Mock(spec=Segment))


def test_post_segment():
    """Test CheckpointManager wrapping segments with post-checkpointing."""
    with get_temp_directory_path() as cp_dir_path:
        cp_manager = CheckpointManager(cp_dir_path)
        cp_manager.post_segment("cpt.txt")(Mock(spec=Segment))


def test_print():
    """Test CheckpointManager string representation methods."""
    with get_temp_directory_path() as cp_dir_path:
        assert isinstance(cp_dir_path, PlatformPath)

        cp_manager = CheckpointManager(cp_dir_path)
        print(cp_manager)
        print(repr(cp_manager))

        cp_manager_2 = eval(repr(cp_manager))
        assert cp_manager_2.dir_path == cp_manager.dir_path
