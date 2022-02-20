#!/usr/bin/env python
#   test/processors/test_height_to_normal.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for HeightToNormalProcessor"""
import numpy as np
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import HeightToNormalProcessor
from pipescaler.testing import (
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
    xfail_unsupported_image_mode,
)


@stage_fixture(
    cls=HeightToNormalProcessor,
    params=[{"sigma": 0.5}, {"sigma": 1.0}],
)
def height_to_normal_processor(request) -> HeightToNormalProcessor:
    return HeightToNormalProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        xfail_unsupported_image_mode()("1"),
        ("L"),
        xfail_unsupported_image_mode()("LA"),
        xfail_unsupported_image_mode()("RGB"),
        xfail_unsupported_image_mode()("RGBA"),
        ("PL"),
        xfail_unsupported_image_mode()("PLA"),
        xfail_unsupported_image_mode()("PRGB"),
        xfail_unsupported_image_mode()("PRGBA"),
    ],
)
def test(infile: str, height_to_normal_processor: HeightToNormalProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        height_to_normal_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            # noinspection PyTypeChecker
            output_datum = np.array(output_image)
            assert output_image.mode == "RGB"
            assert output_image.size == input_image.size
            assert np.min(output_datum[:, :, 2] >= 128)


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("L", "-h"),
        ("L", "--sigma 1.0"),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(HeightToNormalProcessor, args, infile)
