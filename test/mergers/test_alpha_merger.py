#!/usr/bin/env python
#   test/mergers/test_alpha_merger.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaMerger"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import remove_palette_from_image
from pipescaler.mergers import AlphaMerger
from pipescaler.testing import get_infile, stage_fixture, xfail_unsupported_image_mode


@stage_fixture(cls=AlphaMerger, params=[{}])
def merger(request) -> AlphaMerger:
    return AlphaMerger(**request.param)


@pytest.mark.parametrize(
    ("color", "alpha"),
    [
        ("split/LA_color_L", "split/LA_alpha_L"),
        ("split/RGBA_color_RGB", "split/RGBA_alpha_L"),
        ("split/RGBA_color_PRGB", "split/RGBA_alpha_PL"),
        xfail_unsupported_image_mode()("RGB", "RGB"),
        xfail_unsupported_image_mode()("RGB", "RGBA"),
        xfail_unsupported_image_mode()("RGBA", "L"),
        ("split/LA_color_PL", "split/LA_alpha_PL"),
        ("split/RGBA_monochrome_color_RGB", "split/RGBA_monochrome_alpha_1"),
    ],
)
def test(color: str, alpha: str, merger: AlphaMerger) -> None:
    color = get_infile(color)
    alpha = get_infile(alpha)

    with temporary_filename(".png") as outfile:
        color_image = Image.open(color)
        if color_image.mode == "P":
            color_image_mode = remove_palette_from_image(color_image).mode
        else:
            color_image_mode = color_image.mode

        merger(color=color, alpha=alpha, outfile=outfile)
        with Image.open(outfile) as output_image:
            if color_image_mode == "L":
                assert output_image.mode == "LA"
            else:
                assert output_image.mode == "RGBA"
            assert output_image.size == color_image.size
