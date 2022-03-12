#!/usr/bin/env python
#   test/processors/image/test_sharpen.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for SharpenProcessor"""
import numpy as np
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors.image import SharpenProcessor
from pipescaler.testing import (
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
    xfail_unsupported_image_mode,
)


@stage_fixture(cls=SharpenProcessor, params=[{}])
def processor(request) -> SharpenProcessor:
    return SharpenProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        # xfail_unsupported_image_mode()("1"),
        ("L"),
        # xfail_unsupported_image_mode()("LA"),
        ("RGB"),
        # xfail_unsupported_image_mode()("RGBA"),
        # ("PL"),
        # xfail_unsupported_image_mode()("PLA"),
        # ("PRGB"),
        # xfail_unsupported_image_mode()("PRGBA"),
    ],
)
def test(infile: str, processor: SharpenProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size == input_image.size


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(SharpenProcessor, args, infile)
