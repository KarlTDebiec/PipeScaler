#!/usr/bin/env python
#   test/mergers/test_color_match.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for ColorMatchMerger"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import remove_palette_from_image
from pipescaler.mergers import ColorMatchMerger
from pipescaler.testing import get_infile, stage_fixture, xfail_unsupported_image_mode


@stage_fixture(cls=ColorMatchMerger, params=[{}])
def merger(request) -> ColorMatchMerger:
    return ColorMatchMerger(**request.param)


@pytest.mark.parametrize(
    ("reference", "input"),
    [
        xfail_unsupported_image_mode()("alt/L", "L"),
        xfail_unsupported_image_mode()("alt/LA", "LA"),
        ("alt/RGB", "RGB"),
        xfail_unsupported_image_mode()("alt/RGBA", "RGBA"),
        xfail_unsupported_image_mode()("alt/PL", "PL"),
        xfail_unsupported_image_mode()("alt/PLA", "PLA"),
        ("alt/PRGB", "PRGB"),
        xfail_unsupported_image_mode()("alt/PRGBA", "PRGBA"),
    ],
)
def test(reference: str, input: str, merger: ColorMatchMerger):
    reference = get_infile(reference)
    input = get_infile(input)

    with temporary_filename(".png") as outfile:
        input_image = Image.open(input)
        if input_image.mode == "P":
            expected_output_mode = remove_palette_from_image(input_image).mode
        else:
            expected_output_mode = input_image.mode

        merger(reference=reference, input=input, outfile=outfile)

        with Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode
            assert output_image.size == input_image.size
