#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuRunner"""
from pathlib import Path

import pytest

from pipescaler.common import temporary_filename
from pipescaler.runners import WaifuRunner
from pipescaler.testing import get_infile, parametrized_fixture, skip_if_ci


@parametrized_fixture(
    cls=WaifuRunner,
    params=[
        {},
    ],
)
def runner(request) -> WaifuRunner:
    return WaifuRunner(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        skip_if_ci()("RGB"),
    ],
)
def test(infile: str, runner: WaifuRunner) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        outfile = Path(outfile)
        runner.run(infile, outfile)
