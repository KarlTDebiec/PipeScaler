#!/usr/bin/env python
#   test_scripts.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
""""""
from subprocess import Popen

# noinspection PyUnresolvedReferences
from shared import script


def test_help(script: str) -> None:
    command = f"coverage run {script} -h"
    child = Popen(command, shell=True)
    exitcode = child.wait()
    if exitcode != 0:
        raise ValueError()
