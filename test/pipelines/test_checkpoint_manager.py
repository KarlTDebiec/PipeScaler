#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CheckpointManager."""
from __future__ import annotations

from platform import system
from unittest.mock import Mock, patch

from pipescaler.common import PathLike, get_temp_directory_path, validate_output_file
from pipescaler.core.pipelines import PipeObject, Segment
from pipescaler.pipelines import CheckpointManager

if system() == "Windows":
    from pathlib import WindowsPath as PlatformPath

else:
    from pathlib import PosixPath as PlatformPath


def mock_pipe_object_save(path: PathLike) -> None:
    """Save object to file and set path.

    Arguments:
        path: Path to which to save object
    """
    path = validate_output_file(path)
    path.touch()


def mock_pipe_object_save_2(self, path: PathLike) -> None:
    """Save object to file and set path.
    Arguments:
        path: Path to which to save object
    """
    path = validate_output_file(path)
    path.touch()


@patch.object(PipeObject, "save", mock_pipe_object_save_2)
@patch.object(PipeObject, "__abstractmethods__", set())
def test_load_save():
    with get_temp_directory_path() as cp_directory_path:
        cp_manager = CheckpointManager(cp_directory_path)

        # Mocks
        mock_pipe_object_input = Mock(spec=PipeObject)
        mock_pipe_object_input.location_name = "test"
        mock_pipe_object_input.save.side_effect = mock_pipe_object_save

        # Attempt to load single unavailable checkpoint
        outputs = cp_manager.load((mock_pipe_object_input,), ("cpt.txt",))
        assert outputs == None

        # Attempt to load multiple unavailable checkpoints
        outputs = cp_manager.load((mock_pipe_object_input,), ("cpt.txt", "cpt2.txt"))
        assert outputs == None

        # Attempt to load invalid number of checkpoints
        mock_pipe_object_input_2 = Mock(spec=PipeObject)
        mock_pipe_object_input_2.location_name = "test2"
        try:
            outputs = cp_manager.load(
                (mock_pipe_object_input, mock_pipe_object_input_2), ("cpt.txt",)
            )
        except ValueError:
            pass

        # Attempt to save invalid number of checkpoints
        try:
            outputs = cp_manager.save(
                (mock_pipe_object_input,), ("cpt.txt", "cpt2.txt")
            )
        except ValueError:
            pass

        # Save checkpoint
        outputs = cp_manager.save((mock_pipe_object_input,), ("cpt.txt",))
        assert (cp_directory_path / "test" / "cpt.txt").exists()

        # Try to save again, without overwriting
        outputs = cp_manager.save(
            (mock_pipe_object_input,), ("cpt.txt",), overwrite=False
        )
        assert outputs[0].path == (cp_directory_path / "test" / "cpt.txt")

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
        (cp_directory_path / "delete_me.txt").touch()
        (cp_directory_path / "delete_me").mkdir()
        (cp_directory_path / "delete_me" / "delete_me.txt").touch()
        cp_manager.purge_unrecognized_files()


def test_pre_segment():
    with get_temp_directory_path() as cp_directory_path:
        cp_manager = CheckpointManager(cp_directory_path)

        pre_checkpointed_segment = cp_manager.pre_segment("cpt.txt")(Mock(spec=Segment))


def test_post_segment():
    with get_temp_directory_path() as cp_directory_path:
        cp_manager = CheckpointManager(cp_directory_path)

        post_checkpointed_segment = cp_manager.post_segment("cpt.txt")(
            Mock(spec=Segment)
        )


def test_print():
    with get_temp_directory_path() as cp_directory_path:
        assert isinstance(cp_directory_path, PlatformPath)

        cp_manager = CheckpointManager(cp_directory_path)
        print(cp_manager)
        print(repr(cp_manager))

        cp_manager_2 = eval(repr(cp_manager))
        assert cp_manager_2.directory == cp_manager.directory
