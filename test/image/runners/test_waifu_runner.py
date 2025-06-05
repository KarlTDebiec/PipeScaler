#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuRunner."""
from __future__ import annotations

import pytest

from pipescaler.common.file import get_temp_file_path
from pipescaler.image.runners import WaifuRunner
from pipescaler.testing.file import get_test_infile_path
from pipescaler.testing.fixture import parametrized_fixture
from pipescaler.testing.mark import skip_if_ci, skip_if_codex


@parametrized_fixture(
    cls=WaifuRunner,
    params=[
        {},
    ],
)
def runner(request) -> WaifuRunner:
    return WaifuRunner(**request.param)


@pytest.mark.parametrize(
    "infile_name",
    [
        skip_if_codex(skip_if_ci())("RGB"),
    ],
)
def test(infile_name: str, runner: WaifuRunner) -> None:
    input_path = get_test_infile_path(infile_name)

    with get_temp_file_path(".png") as output_path:
        runner.run(input_path, output_path)
