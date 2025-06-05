#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ApngasmRunner."""
from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.common.file import get_temp_file_path
from pipescaler.testing.file import get_test_infile_path
from pipescaler.testing.fixture import parametrized_fixture
from pipescaler.testing.mark import skip_if_ci, skip_if_codex
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
    "infile_names",
    [
        skip_if_codex(skip_if_ci())(["1", "L", "RGB", "RGBA"]),
    ],
)
def test(infile_names: list[str], runner: ApngasmRunner) -> None:
    input_paths = [get_test_infile_path(i) for i in infile_names]

    with get_temp_file_path(".png") as output_path:
        input_paths_str = '"' + '" "'.join([str(i) for i in input_paths]) + '"'
        runner.run(input_paths_str, output_path)

        image = Image.open(output_path)
        assert image.is_animated
        assert image.n_frames == 4
        assert image.info["loop"] == 0
        assert image.info["duration"] == 100.0
