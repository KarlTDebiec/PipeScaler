#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuExternalProcessor"""
import pytest
from PIL import Image

from pipescaler.image.processors import WaifuExternalProcessor
from pipescaler.testing import (
    get_expected_output_mode,
    get_infile,
    parametrized_fixture,
    skip_if_ci,
    xfail_unsupported_image_mode,
)


@parametrized_fixture(
    cls=WaifuExternalProcessor,
    params=[
        {"arguments": "-s 2 -n 1"},
        {"arguments": "-s 1 -n 3"},
    ],
)
def processor(request) -> WaifuExternalProcessor:
    return WaifuExternalProcessor(**request.param)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile"),
    [
        skip_if_ci()("L"),
        skip_if_ci(xfail_unsupported_image_mode())("LA"),
        skip_if_ci()("RGB"),
        skip_if_ci(xfail_unsupported_image_mode())("RGBA"),
        skip_if_ci()("PL"),
        skip_if_ci(xfail_unsupported_image_mode())("PLA"),
        skip_if_ci()("PRGB"),
        skip_if_ci(xfail_unsupported_image_mode())("PRGBA"),
    ],
)
def test(infile: str, processor: WaifuExternalProcessor) -> None:
    infile = get_infile(infile)
    input_image = Image.open(infile)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
