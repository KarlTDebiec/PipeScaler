#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for TexconvRunner."""
from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.common import get_temp_file_path
from pipescaler.image.runners import TexconvRunner
from pipescaler.testing import (
    get_test_infile_path,
    parametrized_fixture,
    xfail_if_platform,
)


@parametrized_fixture(
    cls=TexconvRunner,
    params=[
        {},
    ],
)
def runner(request) -> TexconvRunner:
    return TexconvRunner(**request.param)


@pytest.mark.parametrize(
    ("infile_name"),
    [
        xfail_if_platform({"Darwin", "Linux"})("1"),
        xfail_if_platform({"Darwin", "Linux"})("L"),
        xfail_if_platform({"Darwin", "Linux"})("LA"),
        xfail_if_platform({"Darwin", "Linux"})("RGB"),
        xfail_if_platform({"Darwin", "Linux"})("RGBA"),
        xfail_if_platform({"Darwin", "Linux"})("PL"),
        xfail_if_platform({"Darwin", "Linux"})("PLA"),
        xfail_if_platform({"Darwin", "Linux"})("PRGB"),
        xfail_if_platform({"Darwin", "Linux"})("PRGBA"),
    ],
)
def test(infile_name: str, runner: TexconvRunner) -> None:
    input_path = get_test_infile_path(infile_name)

    with get_temp_file_path(".dds") as output_path:
        runner.run(input_path, output_path)

        with Image.open(input_path) as input_image:
            with Image.open(output_path) as output_image:
                assert output_image.mode == "RGBA"
                assert output_image.size == input_image.size
