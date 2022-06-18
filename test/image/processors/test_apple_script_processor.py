#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for AppleScriptProcessor"""
import pytest
from PIL import Image

from pipescaler.image.processors.apple_script_processor import AppleScriptProcessor
from pipescaler.testing import (
    get_infile,
    parametrized_fixture,
    skip_if_ci,
    xfail_if_platform,
)


@parametrized_fixture(
    cls=AppleScriptProcessor,
    params=[
        {"script": "pixelmator/ml_super_resolution.scpt", "arguments": "2"},
    ],
)
def processor(request) -> AppleScriptProcessor:
    return AppleScriptProcessor(**request.param)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile"),
    [
        skip_if_ci(xfail_if_platform({"Linux", "Windows"}))("RGB"),
        skip_if_ci(xfail_if_platform({"Linux", "Windows"}))("RGBA"),
    ],
)
def test(infile: str, processor: AppleScriptProcessor) -> None:
    infile = get_infile(infile)
    input_image = Image.open(infile)
    output_image = processor(input_image)

    assert output_image.mode == input_image.mode
