#!/usr/bin/env python
#   test/mergers/test_palette_match.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for PaletteMatchMerger"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import get_colors, remove_palette_from_image, validate_image
from pipescaler.mergers import PaletteMatchMerger
from pipescaler.testing import get_infile, stage_fixture, xfail_unsupported_image_mode


@stage_fixture(cls=PaletteMatchMerger, params=[{}])
def merger(request) -> PaletteMatchMerger:
    return PaletteMatchMerger(**request.param)


@pytest.fixture
def reference():
    return r"C:\Users\karls\OneDrive\Desktop\test\one\mode-rgb.png"


@pytest.fixture
def input():
    return r"C:\Users\karls\OneDrive\Desktop\test\one\xbrz-2_xbrz-2.png"


# @pytest.mark.parametrize(
#     ("reference", "input"),
#     [
#         xfail_unsupported_image_mode()("alt/L", "L"),
#         xfail_unsupported_image_mode()("alt/LA", "LA"),
#         ("PRGB", "RGB"),
#         xfail_unsupported_image_mode()("alt/RGBA", "RGBA"),
#         xfail_unsupported_image_mode()("alt/PL", "PL"),
#         xfail_unsupported_image_mode()("alt/PLA", "PLA"),
#         ("alt/PRGB", "PRGB"),
#         xfail_unsupported_image_mode()("alt/PRGBA", "PRGBA"),
#     ],
# )
def test(reference: str, input: str, merger: PaletteMatchMerger):
    # reference = get_infile(reference)
    # input = get_infile(input)

    with temporary_filename(".png") as outfile:
        reference_image = validate_image(reference, "RGB")
        input_image = Image.open(input)
        if input_image.mode == "P":
            expected_output_mode = remove_palette_from_image(input_image).mode
        else:
            expected_output_mode = input_image.mode

        merger(reference=reference, input=input, outfile=outfile)

        with Image.open(outfile) as output_image:
            reference_colors = set(map(tuple, get_colors(reference_image)))
            output_colors = set(map(tuple, get_colors(output_image)))
            assert output_colors.issubset(reference_colors)
            assert output_image.mode == expected_output_mode
            assert output_image.size == input_image.size
