#!/usr/bin/env python
#   test_core.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
from os import listdir
from os.path import basename
from typing import List, Set, Union

import pytest
from shared import infile_subfolders, infiles, xfail_file_not_found

from pipescaler.common import temporary_filename
from pipescaler.core import get_files


@pytest.mark.parametrize(
    ("sources", "style", "exclusions"),
    [
        (infile_subfolders["basic"], "absolute", None),
        (infile_subfolders["basic"], "base", None),
        (infile_subfolders["basic"], "full", None),
        (
            [infile_subfolders["basic"], infile_subfolders["extra"]],
            "base",
            infile_subfolders["basic"],
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
        xfail_file_not_found()(infile_subfolders["basic"], "absolute", None),
        (infile_subfolders["basic"], "base", None),
        (infile_subfolders["basic"], "full", None),
        (
            [infile_subfolders["basic"], infile_subfolders["extra"]],
            "base",
            infile_subfolders["basic"],
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
        (infiles.values(), "absolute", None),
        (infiles.values(), "base", None),
        (infiles.values(), "full", None),
        xfail_file_not_found()(map(basename, infiles.values()), "absolute", None),
        (map(basename, infiles.values()), "base", None),
        (map(basename, infiles.values()), "full", None),
    ],
)
def test_get_files(sources, style, exclusions) -> None:
    get_files(sources, style, exclusions)
