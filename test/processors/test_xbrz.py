#!/usr/bin/env python
#   test/processors/test_xbrz.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for XbrzProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import XbrzProcessor
from pipescaler.testing import (
    expected_output_mode,
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
)


@stage_fixture(
    cls=XbrzProcessor,
    params=[
        {"scale": 2},
    ],
)
def xbrz_processor(request) -> XbrzProcessor:
    return XbrzProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        ("L"),
        ("LA"),
        ("RGB"),
        ("RGBA"),
        ("PL"),
        ("PLA"),
        ("PRGB"),
        ("PRGBA"),
    ],
)
def test(infile: str, xbrz_processor: XbrzProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        xbrz_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] * xbrz_processor.scale,
                input_image.size[1] * xbrz_processor.scale,
            )


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        ("RGB", "--scale 2"),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(XbrzProcessor, args, infile)
