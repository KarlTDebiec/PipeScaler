#!/usr/bin/env python
#   test_gui_processors.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.

import pytest
from PIL import Image
from shared import expected_output_mode, infiles, xfail_if_platform

from pipescaler.common import temporary_filename
from pipescaler.processors import GigapixelAiProcessor


@pytest.fixture()
def gigapixel_ai_processor(request) -> GigapixelAiProcessor:
    return GigapixelAiProcessor(**request.param)


@pytest.mark.gui
@pytest.mark.parametrize(
    ("infile", "gigapixel_ai_processor"),
    [
        xfail_if_platform({"Darwin", "Linux"})(infiles["RGB"], {}),
        xfail_if_platform({"Darwin", "Linux"})(infiles["L"], {}),
    ],
    indirect=["gigapixel_ai_processor"],
)
def test_gigapixel_ai(
    infile: str, gigapixel_ai_processor: GigapixelAiProcessor
) -> None:
    with temporary_filename(".png") as outfile:
        gigapixel_ai_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] * 4,
                input_image.size[1] * 4,
            )
