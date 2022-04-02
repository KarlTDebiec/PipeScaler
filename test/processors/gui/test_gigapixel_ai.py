#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for GigapixelAiProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import GigapixelAiProcessor
from pipescaler.testing import (
    expected_output_mode,
    get_infile,
    skip_if_ci,
    stage_fixture,
    xfail_if_platform,
)


@stage_fixture(
    cls=GigapixelAiProcessor,
    params=[
        {},
    ],
)
def processor(request) -> GigapixelAiProcessor:
    return GigapixelAiProcessor(**request.param)


@pytest.mark.gui
@pytest.mark.parametrize(
    ("infile"),
    [
        skip_if_ci(xfail_if_platform({"Darwin", "Linux"}))("RGB"),
        skip_if_ci(xfail_if_platform({"Darwin", "Linux"}))("L"),
    ],
)
def test(infile: str, processor: GigapixelAiProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] * 4,
                input_image.size[1] * 4,
            )
