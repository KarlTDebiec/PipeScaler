#!/usr/bin/env python
#   test/processors/external/test_texconv.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for TexconvExternalProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import TexconvExternalProcessor
from pipescaler.testing import (
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
    xfail_if_platform,
)


@stage_fixture(
    cls=TexconvExternalProcessor,
    params=[
        {},
    ],
)
def texconv_external_processor(request) -> TexconvExternalProcessor:
    return TexconvExternalProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        xfail_if_platform({"Darwin", "Linux"})("1"),
        xfail_if_platform({"Darwin", "Linux"})("L"),
        xfail_if_platform({"Darwin", "Linux"})("LA"),
        xfail_if_platform({"Darwin", "Linux"})("RGB"),
        xfail_if_platform({"Darwin", "Linux"})("RGBA"),
        xfail_if_platform({"Darwin", "Linux"})("PL"),
        xfail_if_platform({"Darwin", "Linux"})("PLA"),
        xfail_if_platform({"Darwin", "Linux"})("PRGB"),
        xfail_if_platform({"Darwin", "Linux"})("PRGBA"),
    ],
)
def test(infile: str, texconv_external_processor: TexconvExternalProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        texconv_external_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == "RGBA"
            assert output_image.size == input_image.size


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        xfail_if_platform({"Darwin", "Linux"}, raises=ValueError)("RGB", ""),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(TexconvExternalProcessor, args, infile)
