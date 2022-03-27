#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
import pytest

from pipescaler.common import run_command
from pipescaler.testing import get_script


@pytest.mark.parametrize(
    ("script"),
    [
        ("apng_creator.py"),
        ("file_watcher.py"),
        ("pipe_runner.py"),
        ("pipescaler_host.py"),
        ("scaled_image_identifier.py"),
    ],
)
def test_help(script: str) -> None:
    script = get_script(script)

    command = f"coverage run {script} -h"
    run_command(command)
