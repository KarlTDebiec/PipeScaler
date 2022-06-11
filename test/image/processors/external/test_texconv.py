#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for TexconvProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors.external import TexconvRunner
from pipescaler.testing import get_infile, parametrized_fixture, xfail_if_platform


@parametrized_fixture(
    cls=TexconvRunner,
    params=[
        {},
    ],
)
def processor(request) -> TexconvRunner:
    return TexconvRunner(**request.param)


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
def test(infile: str, processor: TexconvRunner) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == "RGBA"
            assert output_image.size == input_image.size
