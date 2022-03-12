#!/usr/bin/env python
#   test/mergers/test_palette_match.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for PaletteMatchMerger"""
import numpy as np
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import remove_palette_from_image, validate_image
from pipescaler.mergers import PaletteMatchMerger
from pipescaler.testing import get_infile, stage_fixture, xfail_unsupported_image_mode


@stage_fixture(cls=PaletteMatchMerger, params=[{}])
def merger(request) -> PaletteMatchMerger:
    return PaletteMatchMerger(**request.param)


@pytest.mark.parametrize(
    ("reference", "input"),
    [
        # xfail_unsupported_image_mode()("alt/L", "L"),
        # xfail_unsupported_image_mode()("alt/LA", "LA"),
        # ("alt/RGB", "RGB"),
        # xfail_unsupported_image_mode()("alt/RGBA", "RGBA"),
        # xfail_unsupported_image_mode()("alt/PL", "PL"),
        # xfail_unsupported_image_mode()("alt/PLA", "PLA"),
        # ("alt/PRGB", "PRGB"),
        # xfail_unsupported_image_mode()("alt/PRGBA", "PRGBA"),
        ("PRGB", "RGB"),
        # ("RGB", "RGB"),
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
            reference_image = validate_image(reference, "RGB")
            reference_colors = np.array(
                [a[1] for a in reference_image.getcolors(16581375)]
            )
            output_colors = np.array([a[1] for a in output_image.getcolors(16581375)])
            assert np.all(reference_colors == output_colors)
            assert output_image.mode == expected_output_mode
            assert output_image.size == input_image.size
