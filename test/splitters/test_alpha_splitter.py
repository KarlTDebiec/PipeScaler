#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaSplitter"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import AlphaMode, MaskFillMode
from pipescaler.splitters import AlphaSplitter
from pipescaler.testing import (
    get_expected_output_mode,
    get_infile,
    parametrized_fixture,
    xfail_unsupported_image_mode,
)


@parametrized_fixture(
    cls=AlphaSplitter,
    params=[
        {
            "alpha_mode": AlphaMode.GRAYSCALE,
            "mask_fill_mode": None,
        },
        {
            "alpha_mode": AlphaMode.MONOCHROME_OR_GRAYSCALE,
            "mask_fill_mode": None,
        },
        {
            "alpha_mode": AlphaMode.MONOCHROME_OR_GRAYSCALE,
            "mask_fill_mode": MaskFillMode.BASIC,
        },
        {
            "alpha_mode": AlphaMode.MONOCHROME_OR_GRAYSCALE,
            "mask_fill_mode": MaskFillMode.MATCH_PALETTE,
        },
    ],
)
def splitter(request) -> AlphaSplitter:
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
def test(infile: str, splitter: AlphaSplitter) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as color_outfile:
        with temporary_filename(".png") as alpha_outfile:
            input_image = Image.open(infile)
            expected_color_mode = get_expected_output_mode(input_image).rstrip("A")

            splitter(infile, color=color_outfile, alpha=alpha_outfile)

            with Image.open(color_outfile) as color_image:
                assert color_image.mode == expected_color_mode
                assert color_image.size == input_image.size

            with Image.open(alpha_outfile) as alpha_image:
                assert alpha_image.size == input_image.size
