#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuRunner."""
from __future__ import annotations

import pytest

from pipescaler.common import get_temp_file_path
from pipescaler.image.runners import WaifuRunner
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
    ("infile_name"),
    [
        skip_if_ci()("RGB"),
    ],
)
def test(infile_name: str, runner: WaifuRunner) -> None:
    input_path = get_test_infile_path(infile_name)

    with get_temp_file_path(".png") as output_path:
        runner.run(input_path, output_path)
