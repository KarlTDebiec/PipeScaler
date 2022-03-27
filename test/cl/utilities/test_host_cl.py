#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for HostCL."""
from __future__ import annotations

from inspect import getfile

from pytest import fixture, mark

from pipescaler.cl.utilities import HostCL
from pipescaler.common import run_command


@fixture
def script(request) -> str:
    return getfile(HostCL)


@mark.parametrize(
    ("args"),
    [
        ("-h"),
    ],
)
def test(script: str, args: str) -> None:
    command = f"coverage run {script} {args}"
    run_command(command)
