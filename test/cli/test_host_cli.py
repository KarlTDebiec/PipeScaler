#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for HostCli."""
from __future__ import annotations

from inspect import getfile
from signal import SIGTERM
from subprocess import PIPE, Popen

from pytest import fixture

from pipescaler.cli.utilities import HostCli
from pipescaler.common import get_temp_file_path


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
    return getfile(HostCli)


def test(script, conf: str) -> None:
    with get_temp_file_path(".yml") as conf_path:
        with open(conf_path, "w") as conf_file:
            conf_file.write(conf)

        command = f"coverage run {getfile(HostCli)} {conf_path}"
        with Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as child:
            if child.stderr is not None:
                child.stderr.readline()
                child.send_signal(SIGTERM)
