#!/usr/bin/env python
#   test_core.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
from os.path import dirname, join

import pytest

from pipescaler.common import package_root
from pipescaler.core import parse_file_list

infile_directories = {
    directory: join(dirname(package_root), "test", "data", "infiles", directory)
    for directory in ["alt", "basic", "extra", "novel", "split"]
}


@pytest.mark.parametrize(
    ("files", "absolute_paths", "exclusions"),
    [
        (infile_directories["basic"], False, None),
        ([infile_directories["alt"], infile_directories["basic"]], False, None),
        (infile_directories["alt"], False, infile_directories["basic"]),
        ([infile_directories["alt"], infile_directories["basic"]], True, None),
        (infile_directories["basic"], True, None),
    ],
)
def test_parse_file_list_directory(files, absolute_paths, exclusions) -> None:
    nay = parse_file_list(files, absolute_paths, exclusions)
    print(nay)


@pytest.mark.parametrize(
    ("files", "absolute_paths", "exclusions"),
    [
        (infile_directories["basic"], False, None),
        ([infile_directories["alt"], infile_directories["basic"]], False, None),
        (infile_directories["alt"], False, infile_directories["basic"]),
        ([infile_directories["alt"], infile_directories["basic"]], True, None),
        (infile_directories["basic"], True, None),
    ],
)
def test_parse_file_list_directory(files, absolute_paths, exclusions) -> None:
    nay = parse_file_list(files, absolute_paths, exclusions)
    print(nay)
