#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ApngasmRunner."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.common import ExecutableNotFoundError
from pipescaler.common.file import get_temp_file_path
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture
from pipescaler.testing.mark import skip_if_ci, skip_if_codex, xfail_if_platform
from pipescaler.video.runners import ApngasmRunner


@parametrized_fixture(
    cls=ApngasmRunner,
    params=[
        {},
    ],
)
def runner(request) -> ApngasmRunner:
    return ApngasmRunner(**request.param)


@pytest.mark.parametrize(
    "input_filenames",
    [
        skip_if_codex(
            skip_if_ci(xfail_if_platform({"Windows"}, ExecutableNotFoundError))
        )(["1", "L", "RGB", "RGBA"]),
    ],
)
def test(input_filenames, runner: ApngasmRunner):
    input_paths = [get_test_input_path(i) for i in input_filenames]

    with get_temp_file_path(".png") as output_path:
        input_paths_str = '"' + '" "'.join([str(i) for i in input_paths]) + '"'
        runner.run(input_paths_str, output_path)

        image = Image.open(output_path)
        assert image.is_animated
        assert image.n_frames == 4
        assert image.info["loop"] == 0
        assert image.info["duration"] == 100.0
