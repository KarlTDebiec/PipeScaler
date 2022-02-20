#!/usr/bin/env python
#   test/splitters/test_alpha_splitter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for AlphaSplitter"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import remove_palette_from_image
from pipescaler.splitters import AlphaSplitter
from pipescaler.testing import get_infile, stage_fixture, xfail_unsupported_image_mode


@stage_fixture(
    cls=AlphaSplitter,
    params=[
        {"alpha_mode": "L"},
        {"alpha_mode": "L_OR_1"},
        {"alpha_mode": "L_OR_1_FILL"},
    ],
)
def alpha_splitter(request) -> AlphaSplitter:
    return AlphaSplitter(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        xfail_unsupported_image_mode()("1"),
        xfail_unsupported_image_mode()("L"),
        ("LA"),
        xfail_unsupported_image_mode()("RGB"),
        ("RGBA"),
        ("PLA"),
        ("PRGBA"),
        ("novel/RGBA_monochrome"),
    ],
)
def test(
    infile: str,
    alpha_splitter: AlphaSplitter,
) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as color_outfile:
        with temporary_filename(".png") as alpha_outfile:
            input_image = Image.open(infile)
            if input_image.mode == "P":
                expected_color_mode = remove_palette_from_image(
                    input_image
                ).mode.rstrip("A")
            else:
                expected_color_mode = input_image.mode.rstrip("A")

            alpha_splitter(infile, color=color_outfile, alpha=alpha_outfile)

            with Image.open(color_outfile) as color_image:
                assert color_image.mode == expected_color_mode
                assert color_image.size == input_image.size

            with Image.open(alpha_outfile) as alpha_image:
                assert alpha_image.size == input_image.size
