#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for FileScanner."""
import logging
from os import mkdir
from pathlib import Path
from tempfile import TemporaryDirectory

from pipescaler.common import DirectoryNotFoundError
from pipescaler.utilities import FileScanner

logging.getLogger().setLevel(level=logging.DEBUG)
from pytest import mark


@mark.xfail(raises=DirectoryNotFoundError)
def test_directory_not_found():
    file_scanner = FileScanner("do", "not", "exist")


def test():
    with TemporaryDirectory() as project_root:
        project_root = Path(project_root)
        mkdir(project_root.joinpath("input_1"))
        mkdir(project_root.joinpath("input_2"))
        mkdir(project_root.joinpath("reviewed"))
        mkdir(project_root.joinpath("ignored"))

        file_scanner = FileScanner(
            project_root,
            [
                project_root.joinpath("input_1"),
                project_root.joinpath("input_2"),
                project_root.joinpath("input_3"),
            ],
            project_root.joinpath("reviewed"),
        )
