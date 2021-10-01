#!/usr/bin/env python
#   test_scripts.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.

from pipescaler.common import run_command

# noinspection PyUnresolvedReferences
from shared import script


def test_help(script: str) -> None:
    command = f"coverage run {script} -h"
    exitcode, stdout, stderr = run_command(command)
    assert exitcode == 0
