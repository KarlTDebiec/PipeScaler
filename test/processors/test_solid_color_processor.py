#!/usr/bin/env python
#   test/processors/test_solid_color_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for SolidColorProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import SolidColorProcessor
from pipescaler.testing import (
    expected_output_mode,
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
)


@stage_fixture(cls=SolidColorProcessor, params=[{}])
def solid_color_processor(request) -> SolidColorProcessor:
    return SolidColorProcessor(**request.param)


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
def test(infile: str, solid_color_processor: SolidColorProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        solid_color_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == input_image.size
            assert len(output_image.getcolors()) == 1


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        ("RGB", ""),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(SolidColorProcessor, args, infile)
