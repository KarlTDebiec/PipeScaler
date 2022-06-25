#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for FileScanner."""
import logging
from os import mkdir
from shutil import copy

from pipescaler.common.file import temp_directory
from pipescaler.testing import get_infile, get_sub_directory
from pipescaler.utilities import FileScanner

logging.getLogger().setLevel(level=logging.DEBUG)


def test():
    with temp_directory() as project_root, temp_directory() as input_directory:
        # Stage input directory
        for infile in get_sub_directory().iterdir():
            copy(infile, input_directory.joinpath(infile.name))

        mkdir(project_root.joinpath("reviewed"))
        infile = get_infile("L")
        copy(infile, project_root.joinpath("reviewed", infile.name))

        mkdir(project_root.joinpath("ignore"))
        infile = get_infile("LA")
        copy(infile, project_root.joinpath("ignore", infile.name))

        mkdir(project_root.joinpath("review"))
        infile = get_infile("RGB")
        copy(infile, project_root.joinpath("review", infile.name))

        mkdir(project_root.joinpath("remove"))
        infile = get_infile("1")
        copy(infile, project_root.joinpath("remove", infile.name))

        mkdir(project_root.joinpath("new"))
        infile = get_infile("RGBA")
        copy(infile, project_root.joinpath("new", infile.name))

        file_scanner = FileScanner(
            project_root,
            [input_directory],
            project_root.joinpath("reviewed"),
            rules=[
                ("L", "move"),
                ("LA", "ignore"),
            ],
        )
        file_scanner()
