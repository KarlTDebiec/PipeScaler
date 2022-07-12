#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuSerializer."""
from __future__ import annotations

from pytest import fixture, mark

from pipescaler.common import get_temp_file_path
from pipescaler.testing import get_test_model_infile_path, skip_if_ci
from pipescaler.utilities import WaifuSerializer


@fixture
def utility(request) -> WaifuSerializer:
    return WaifuSerializer()


@mark.parametrize(
    ("architecture", "infile"),
    [
        skip_if_ci()("upconv7", "WaifuUpConv7/a-2-1.json"),
        skip_if_ci()("vgg7", "WaifuVgg7/a-2-1.json"),
    ],
)
def test(architecture: str, infile: str, utility: WaifuSerializer) -> None:
    input_path = get_test_model_infile_path(infile)
    with get_temp_file_path(".pth") as output_path:
        utility(architecture, input_path, output_path)
