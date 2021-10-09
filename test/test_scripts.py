#!/usr/bin/env python
#   test_scripts.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
from os.path import join

import pytest

from pipescaler.common import package_root, run_command

scripts = {
    f: join(package_root, "scripts", f)
    for f in [
        "apng_creator.py",
        "directory_watcher.py",
        "pipe_runner.py",
        "pipescaler_host.py",
        "scaled_image_identifier.py",
    ]
}


@pytest.fixture(params=scripts.keys())
def script(request):
    return scripts[request.param]


def test_help(script: str) -> None:
    command = f"coverage run {script} -h"
    run_command(command)
