#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for AppleScriptProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import AppleScriptProcessor
from pipescaler.testing import (
    get_infile,
    parametrized_fixture,
    skip_if_ci,
    xfail_if_platform,
)


@parametrized_fixture(
    cls=AppleScriptProcessor,
    params=[
        {"script": "pixelmator/ml_super_resolution.scpt", "args": "2"},
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

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size == (
                input_image.size[0] * int(processor.args),
                input_image.size[1] * int(processor.args),
            )
