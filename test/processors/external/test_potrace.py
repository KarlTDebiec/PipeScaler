#!/usr/bin/env python
#   test/processors/external/test_potrace.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for PotraceExternalProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import PotraceExternalProcessor
from pipescaler.testing import (
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
    xfail_unsupported_image_mode,
)


@stage_fixture(
    cls=PotraceExternalProcessor,
    params=[
        {},
        {"scale": 2},
    ],
)
def potrace_external_processor(request) -> PotraceExternalProcessor:
    return PotraceExternalProcessor(**request.param)


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
def test(infile: str, potrace_external_processor: PotraceExternalProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        potrace_external_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == "L"
            assert output_image.size == (
                input_image.size[0] * potrace_external_processor.scale,
                input_image.size[1] * potrace_external_processor.scale,
            )


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        ("L", ""),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(PotraceExternalProcessor, args, infile)
