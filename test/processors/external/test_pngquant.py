#!/usr/bin/env python
#   test/processors/external/test_pngquant.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for PngquantProcessor"""
from os.path import getsize

import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import PngquantProcessor
from pipescaler.testing import get_infile, run_processor_on_command_line, stage_fixture


@stage_fixture(
    cls=PngquantProcessor,
    params=[
        {},
    ],
)
def processor(request) -> PngquantProcessor:
    return PngquantProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        ("1"),
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
def test(infile: str, processor: PngquantProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode in (input_image.mode, "P")
            assert output_image.size == input_image.size
            assert getsize(outfile) <= getsize(infile)


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        ("RGB", ""),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(PngquantProcessor, args, infile)
