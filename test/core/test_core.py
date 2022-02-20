#!/usr/bin/env python
#   test/core/test_core.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for core"""
from os import listdir
from os.path import basename
from typing import List, Set, Union

import pytest

from pipescaler.common import temporary_filename
from pipescaler.core import get_files
from pipescaler.testing import get_sub_directory, xfail_file_not_found

infiles = get_files(get_sub_directory("basic"), style="absolute")


@pytest.mark.parametrize(
    ("sources", "style", "exclusions"),
    [
        (get_sub_directory("basic"), "absolute", None),
        (get_sub_directory("basic"), "base", None),
        (get_sub_directory("basic"), "full", None),
        (
            [get_sub_directory("basic"), get_sub_directory("extra")],
            "base",
            get_sub_directory("basic"),
        ),
    ],
)
def test_get_files_in_directory(
    sources: Union[str, List[str]], style: str, exclusions: Set[str]
) -> None:
    get_files(sources, style, exclusions)


@pytest.mark.parametrize(
    ("sources", "style", "exclusions"),
    [
        xfail_file_not_found()(get_sub_directory("basic"), "absolute", None),
        (get_sub_directory("basic"), "base", None),
        (get_sub_directory("basic"), "full", None),
        (
            [get_sub_directory("basic"), get_sub_directory("extra")],
            "base",
            get_sub_directory("basic"),
        ),
    ],
)
def test_get_files_in_text_file(sources, style, exclusions) -> None:
    with temporary_filename(".txt") as text_file_name:
        with open(text_file_name, "w") as text_file:
            if isinstance(sources, str):
                sources = [sources]
            for source in sources:
                for filename in listdir(source):
                    text_file.write(f"{filename}\n")
        get_files(text_file_name, style, exclusions)


@pytest.mark.parametrize(
    ("sources", "style", "exclusions"),
    [
        (infiles, "absolute", None),
        (infiles, "base", None),
        (infiles, "full", None),
        xfail_file_not_found()(map(basename, infiles), "absolute", None),
        (map(basename, infiles), "base", None),
        (map(basename, infiles), "full", None),
    ],
)
def test_get_files(sources, style, exclusions) -> None:
    get_files(sources, style, exclusions)
