#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PotraceRunner."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.common.file import get_temp_file_path
from pipescaler.image.runners import PotraceRunner
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=PotraceRunner,
    params=[
        {},
    ],
)
def runner(request) -> PotraceRunner:
    return PotraceRunner(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        "L",
    ],
)
def test(input_filename: str, runner: PotraceRunner) -> None:
    input_path = get_test_input_path(input_filename)

    with get_temp_file_path(".bmp") as bmp_path:
        Image.open(input_path).save(bmp_path)
        with get_temp_file_path(".svg") as output_path:
            runner.run(bmp_path, output_path)
