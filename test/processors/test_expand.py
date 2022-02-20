#!/usr/bin/env python
#   test/processors/test_expand.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for ExpandProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import ExpandProcessor
from pipescaler.testing import get_infile, run_processor_on_command_line, stage_fixture


@stage_fixture(
    cls=ExpandProcessor,
    params=[
        {"pixels": (4, 4, 4, 4)},
    ],
)
def expand_processor(request) -> ExpandProcessor:
    return ExpandProcessor(**request.param)


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
def test(infile: str, expand_processor: ExpandProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        expand_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size == (
                input_image.size[0] + expand_processor.left + expand_processor.right,
                input_image.size[1] + expand_processor.top + expand_processor.bottom,
            )


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        ("RGB", "--pixels 4 4 4 4"),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(ExpandProcessor, args, infile)
