#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for FileScanner."""
from os import mkdir
from pathlib import Path
from shutil import copy

from pipescaler import FileScanner
from pipescaler.common import get_temp_directory_path
from pipescaler.testing import get_test_infile_directory_path, get_test_infile_path


def stage_files(input_directory: Path, project_root: Path) -> None:
    for infile in get_test_infile_directory_path().iterdir():
        copy(infile, input_directory / infile.name)

    mkdir(project_root / "reviewed")
    infile = get_test_infile_path("L")
    copy(infile, project_root / "reviewed" / infile.name)

    mkdir(project_root / "ignore")
    infile = get_test_infile_path("LA")
    copy(infile, project_root / "ignore" / infile.name)

    mkdir(project_root / "review")
    infile = get_test_infile_path("RGB")
    copy(infile, project_root / "review" / infile.name)

    mkdir(project_root / "remove")
    infile = get_test_infile_path("1")
    copy(infile, project_root / "remove" / infile.name)

    mkdir(project_root / "new")
    infile = get_test_infile_path("RGBA")
    copy(infile, project_root / "new" / infile.name)


def test():
    with get_temp_directory_path() as input_directory, get_temp_directory_path() as project_root:
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
    with get_temp_directory_path() as input_directory, get_temp_directory_path() as project_root:
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
    with get_temp_directory_path() as input_directory, get_temp_directory_path() as project_root:
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
