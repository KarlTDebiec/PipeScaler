#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuRunner."""
from pathlib import Path

import pytest

from pipescaler.common import get_temp_file_path
from pipescaler.runners import WaifuRunner
from pipescaler.testing import get_test_infile_path, parametrized_fixture, skip_if_ci


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
    input_path: Path = get_test_infile_path(infile)

    with get_temp_file_path(".png") as output_path:
        runner.run(input_path, output_path)
