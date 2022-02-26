#!/usr/bin/env python
#   test/processors/image/test_threshold.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for ThresholdProcessor"""
import numpy as np
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import ThresholdProcessor
from pipescaler.testing import (
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
    xfail_unsupported_image_mode,
)


@stage_fixture(
    cls=ThresholdProcessor,
    params=[
        {"threshold": 128, "denoise": False},
        {"threshold": 128, "denoise": True},
    ],
)
def processor(request) -> ThresholdProcessor:
    return ThresholdProcessor(**request.param)


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
def test(infile: str, processor: ThresholdProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            # noinspection PyTypeChecker
            output_datum = np.array(output_image)
            assert output_image.mode == "L"
            assert output_image.size == input_image.size
            assert np.logical_or(output_datum == 0, output_datum == 255).all()


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        ("L", ""),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(ThresholdProcessor, args, infile)
