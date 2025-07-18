#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaSplitter."""

import pytest
from PIL import Image

from pipescaler.image.core import AlphaMode, MaskFillMode
from pipescaler.image.operators.splitters import AlphaSplitter
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


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
    "input_filename",
    [
        xfail_unsupported_image_mode()("1"),
        xfail_unsupported_image_mode()("L"),
        "LA",
        xfail_unsupported_image_mode()("RGB"),
        "RGBA",
        "PLA",
        "PRGBA",
        "novel/RGBA_monochrome",
    ],
)
def test(input_filename, splitter: AlphaSplitter) -> None:
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    color_img, alpha_img = splitter(input_img)

    assert color_img.mode in splitter.outputs()["color"]
    assert color_img.mode == get_expected_output_mode(input_img).rstrip("A")
    assert color_img.size == input_img.size
    assert alpha_img.mode in splitter.outputs()["alpha"]
    assert alpha_img.size == input_img.size
