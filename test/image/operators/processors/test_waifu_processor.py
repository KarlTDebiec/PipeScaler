#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuProcessor."""
import pytest
from PIL import Image

from pipescaler.image import get_expected_output_mode, xfail_unsupported_image_mode
from pipescaler.image.operators.processors import WaifuProcessor
from pipescaler.testing import (
    get_test_infile_path,
    get_test_model_infile_path,
    skip_if_ci,
)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile", "model"),
    [
        skip_if_ci(xfail_unsupported_image_mode())("1", "WaifuUpConv7/a-2-3"),
        skip_if_ci()("L", "WaifuUpConv7/a-2-3"),
        skip_if_ci(xfail_unsupported_image_mode())("LA", "WaifuUpConv7/a-2-3"),
        skip_if_ci()("RGB", "WaifuUpConv7/a-2-3"),
        skip_if_ci()("RGB", "WaifuVgg7/a-1-3"),
        skip_if_ci(xfail_unsupported_image_mode())("RGBA", "WaifuUpConv7/a-2-3"),
    ],
)
def test(infile: str, model: str) -> None:
    processor = WaifuProcessor(model_infile=get_test_model_infile_path(model))

    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
