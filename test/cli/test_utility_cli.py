#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for UtilitiesCli."""
from __future__ import annotations

from inspect import getfile

from pytest import fixture, mark

from pipescaler.cli import UtilitiesCli
from pipescaler.common import run_command
from pipescaler.testing import xfail_value


@fixture
def script(request) -> str:
    return getfile(UtilitiesCli)


@mark.parametrize(
    ("args"),
    [
        xfail_value()(""),
        ("-h"),
        ("apngcreator -h"),
        ("esrganserializer -h"),
        ("host -h"),
        ("waifuserializer -h"),
    ],
)
def test(script: str, args: str) -> None:
    command = f"coverage run {script} {args}"
    run_command(command)
