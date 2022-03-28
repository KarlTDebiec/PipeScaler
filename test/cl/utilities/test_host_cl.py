#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for HostCL."""
from __future__ import annotations

from inspect import getfile
from signal import SIGTERM
from subprocess import PIPE, Popen

from pytest import fixture, mark

from pipescaler.cl.utilities import HostCL
from pipescaler.common import run_command, temporary_filename


@fixture()
def conf():
    return """
stages:
    xbrz-2:
        XbrzProcessor:
            scale: 2
"""


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


@mark.parametrize(
    ("args"),
    [
        (""),
    ],
)
def test_conf(script: str, conf: str, args: str) -> None:
    with temporary_filename(".yml") as conf_outfile_name:
        with open(conf_outfile_name, "w") as conf_outfile:
            conf_outfile.write(conf)

        command = f"coverage run {getfile(HostCL)} {conf_outfile_name}"
        with Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as child:
            child.stderr.readline()
            child.send_signal(SIGTERM)
