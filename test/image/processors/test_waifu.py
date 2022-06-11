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


@parametrized_fixture(
    cls=WaifuProcessor,
    params=[
        {"model_infile": get_model_infile("WaifuUpConv7/a-2-3")},
        {"model_infile": get_model_infile("WaifuVgg7/a-1-3")},
    ],
)
def processor(request) -> WaifuProcessor:
    return WaifuProcessor(**request.param)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile"),
    [
        skip_if_ci(xfail_unsupported_image_mode())("1"),
        skip_if_ci()("L"),
        skip_if_ci(xfail_unsupported_image_mode())("LA"),
        skip_if_ci()("RGB"),
        skip_if_ci(xfail_unsupported_image_mode())("RGBA"),
    ],
)
def test(infile: str, processor: WaifuProcessor) -> None:
    infile = get_infile(infile)
    input_image = Image.open(infile)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
