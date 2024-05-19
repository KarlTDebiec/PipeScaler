#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for NormalSplitter"""
import pytest
from PIL import Image

from pipescaler.image.operators.splitters import NormalSplitter
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_infile_path
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
    "infile",
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
def test(infile: str, splitter: NormalSplitter) -> None:
    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    x_image, y_image, z_image = splitter(input_image)

    assert x_image.mode == "L"
    assert x_image.size == input_image.size
    assert y_image.mode == "L"
    assert y_image.size == input_image.size
    assert z_image.mode == "L"
    assert z_image.size == input_image.size
