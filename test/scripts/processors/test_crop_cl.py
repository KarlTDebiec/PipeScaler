#!/usr/bin/env python
#   test/scripts/processors/test_crop_cl.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
from __future__ import annotations

from inspect import getfile

from pytest import fixture, mark

from pipescaler.common import run_command, temporary_filename
from pipescaler.scripts.processors import CropCommandLineTool
from pipescaler.testing import get_infile


@fixture
def script(request) -> str:
    return getfile(CropCommandLineTool)


@mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        ("RGB", "--pixels 4 4 4 4"),
    ],
)
def test(script: str, infile: str, args: str) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        command = f"coverage run {script} {args} {infile} {outfile}"
        run_command(command)