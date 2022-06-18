#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuProcessor."""
import pytest
from PIL import Image

from pipescaler.image.processors import WaifuProcessor
from pipescaler.testing import (
    get_expected_output_mode,
    get_infile,
    get_model_infile,
    parametrized_fixture,
    skip_if_ci,
    xfail_unsupported_image_mode,
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
    processor = WaifuProcessor(model_infile=get_model_infile(model))

    infile = get_infile(infile)
    input_image = Image.open(infile)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
