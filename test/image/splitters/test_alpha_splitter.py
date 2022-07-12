#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaSplitter."""
import pytest
from PIL import Image

from pipescaler.core.enums import AlphaMode, MaskFillMode
from pipescaler.image.splitters import AlphaSplitter
from pipescaler.testing import (
    get_expected_output_mode,
    get_test_infile_path,
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
    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    color_image, alpha_image = splitter(input_image)

    assert color_image.mode in splitter.outputs["color"]
    assert color_image.mode == get_expected_output_mode(input_image).rstrip("A")
    assert color_image.size == input_image.size
    assert alpha_image.mode in splitter.outputs["alpha"]
    assert alpha_image.size == input_image.size
