#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for NormalSplitter."""

import pytest
from PIL import Image

from pipescaler.image.operators.splitters import NormalSplitter
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=NormalSplitter,
    params=[
        {},
    ],
)
def splitter(request) -> NormalSplitter:
    return NormalSplitter(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        xfail_unsupported_image_mode()("1"),
        xfail_unsupported_image_mode()("L"),
        xfail_unsupported_image_mode()("LA"),
        "RGB",
        xfail_unsupported_image_mode()("RGBA"),
        "PRGB",
        "novel/RGB_normal",
    ],
)
def test(input_filename: str, splitter: NormalSplitter):
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    x_img, y_img, z_img = splitter(input_img)

    assert x_img.mode == "L"
    assert x_img.size == input_img.size
    assert y_img.mode == "L"
    assert y_img.size == input_img.size
    assert z_img.mode == "L"
    assert z_img.size == input_img.size
