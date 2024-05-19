#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuSerializer."""
from __future__ import annotations

from pytest import fixture, mark

from pipescaler.common.file import get_temp_file_path
from pipescaler.image.utilities import WaifuSerializer
from pipescaler.testing.file import get_test_model_infile_path
from pipescaler.testing.mark import skip_if_ci


@fixture
def utility(request) -> WaifuSerializer:
    return WaifuSerializer()


@mark.parametrize(
    ("architecture", "infile"),
    [
        skip_if_ci()("upconv7", "WaifuUpConv7/a-2-1.json"),
        skip_if_ci()("vgg7", "WaifuVgg7/a-2-0.json"),
    ],
)
def test(architecture: str, infile: str, utility: WaifuSerializer) -> None:
    input_path = get_test_model_infile_path(infile)

    with get_temp_file_path(".pth") as output_path:
        utility.run(architecture, input_path, output_path)
