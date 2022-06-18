#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for PotraceRunner"""
from pathlib import Path

import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.runners import PotraceRunner
from pipescaler.testing import get_infile, parametrized_fixture


@parametrized_fixture(
    cls=PotraceRunner,
    params=[
        {},
    ],
)
def runner(request) -> PotraceRunner:
    return PotraceRunner(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        ("L"),
    ],
)
def test(infile: str, runner: PotraceRunner) -> None:
    infile = get_infile(infile)

    with temporary_filename(".bmp") as bmp_infile:
        Image.open(infile).save(bmp_infile)
        with temporary_filename(".svg") as outfile:
            outfile = Path(outfile)
            runner.run(bmp_infile, outfile)
