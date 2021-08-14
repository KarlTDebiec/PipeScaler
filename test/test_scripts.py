#!/usr/bin/env python
#   test_scripts.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
####################################### MODULES ########################################
from os.path import join
from subprocess import Popen

import pytest

from pipescaler.common import package_root

###################################### VARIABLES #######################################
scripts = {
    f: join(package_root, "scripts", f)
    for f in [
        "apng_creator.py",
        "directory_watcher.py",
        "pipe_runner.py",
        "scaled_image_identifier.py",
    ]
}


####################################### FIXTURES #######################################
@pytest.fixture(params=scripts.keys())
def script(request):
    return scripts[request.param]


######################################## TESTS #########################################
def test_help(script: str) -> None:
    command = f"coverage run {script} -h"
    child = Popen(command, shell=True)
    exitcode = child.wait()
    if exitcode != 0:
        raise ValueError()
