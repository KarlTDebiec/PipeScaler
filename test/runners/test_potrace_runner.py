#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for PotraceRunner."""
from pathlib import Path

import pytest
from PIL import Image

from pipescaler.common import get_temp_file_path
from pipescaler.runners import PotraceRunner
from pipescaler.testing import get_test_infile_path, parametrized_fixture


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
    input_path: Path = get_test_infile_path(infile)

    with get_temp_file_path(".bmp") as bmp_path:
        Image.open(input_path).save(bmp_path)
        with get_temp_file_path(".svg") as output_path:
            runner.run(bmp_path, output_path)
