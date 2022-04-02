#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for EsrganCli."""
from __future__ import annotations

from inspect import getfile

from pytest import fixture, mark

from pipescaler.cli.processors import EsrganCli
from pipescaler.common import run_command, temporary_filename
from pipescaler.testing import get_infile, get_model_infile, skip_if_ci


@fixture
def script(request) -> str:
    return getfile(EsrganCli)


@mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        skip_if_ci()("RGB", f"--model {get_model_infile('ESRGAN/1x_BC1-smooth2')}"),
    ],
)
def test(script: str, infile: str, args: str) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        command = f"coverage run {script} {args} {infile} {outfile}"
        run_command(command)
