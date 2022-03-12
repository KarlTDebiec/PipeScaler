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
from pipescaler.core import remove_palette_from_image
from pipescaler.mergers import PaletteMatchMerger
from pipescaler.testing import get_infile, stage_fixture


@stage_fixture(cls=PaletteMatchMerger, params=[{}])
def merger(request) -> PaletteMatchMerger:
    return PaletteMatchMerger(**request.param)


@pytest.mark.parametrize(
    ("reference", "input"),
    [
        ("alt/L", "L"),
        ("alt/LA", "LA"),
        ("alt/RGB", "RGB"),
        ("alt/RGBA", "RGBA"),
        ("alt/PL", "PL"),
        ("alt/PLA", "PLA"),
        ("alt/PRGB", "PRGB"),
        ("alt/PRGBA", "PRGBA"),
    ],
)
def test(reference: str, input: str, merger: PaletteMatchMerger):
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
