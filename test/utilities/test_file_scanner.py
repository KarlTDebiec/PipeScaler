#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for FileScanner."""

from os import mkdir
from pathlib import Path
from shutil import copy

from pipescaler import FileScanner
from pipescaler.common.file import get_temp_directory_path
from pipescaler.testing.file import get_test_input_dir_path, get_test_input_path


def stage_files(input_directory: Path, project_root: Path):
    """Stage test files in temporary directories.

    Arguments:
        input_directory: Directory for input files
        project_root: Project root directory
    """
    for input_path in get_test_input_dir_path().iterdir():
        copy(input_path, input_directory / input_path.name)

    mkdir(project_root / "reviewed")
    input_path = get_test_input_path("L")
    copy(input_path, project_root / "reviewed" / input_path.name)

    mkdir(project_root / "ignore")
    input_path = get_test_input_path("LA")
    copy(input_path, project_root / "ignore" / input_path.name)

    mkdir(project_root / "review")
    input_path = get_test_input_path("RGB")
    copy(input_path, project_root / "review" / input_path.name)

    mkdir(project_root / "remove")
    input_path = get_test_input_path("1")
    copy(input_path, project_root / "remove" / input_path.name)

    mkdir(project_root / "new")
    input_path = get_test_input_path("RGBA")
    copy(input_path, project_root / "new" / input_path.name)


def test():
    """Test FileScanner organizing files based on rules."""
    with (
        get_temp_directory_path() as input_directory,
        get_temp_directory_path() as project_root,
    ):
        stage_files(input_directory, project_root)

        file_scanner = FileScanner(
            [input_directory],
            project_root,
            project_root / "reviewed",
            rules=[
                ("^PL$", "move"),
                ("^PLA$", "remove"),
            ],
        )
        file_scanner()


def test_remove_prefix():
    """Test FileScanner with prefix removal option."""
    with (
        get_temp_directory_path() as input_directory,
        get_temp_directory_path() as project_root,
    ):
        stage_files(input_directory, project_root)

        file_scanner = FileScanner(
            [input_directory],
            project_root,
            project_root / "reviewed",
            rules=[
                ("^PL$", "move"),
                ("^PLA$", "remove"),
            ],
            remove_prefix="P",
        )
        file_scanner()


def test_output_format():
    """Test FileScanner with output format conversion."""
    with (
        get_temp_directory_path() as input_directory,
        get_temp_directory_path() as project_root,
    ):
        stage_files(input_directory, project_root)

        file_scanner = FileScanner(
            [input_directory],
            project_root,
            project_root / "reviewed",
            rules=[
                ("^PL$", "move"),
                ("^PLA$", "remove"),
            ],
            output_format="bmp",
        )
        file_scanner()
