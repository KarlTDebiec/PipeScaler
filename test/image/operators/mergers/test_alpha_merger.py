#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaMerger."""

import pytest
from PIL import Image

from pipescaler.image.operators.mergers import AlphaMerger
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=AlphaMerger,
    params=[
        {},
    ],
)
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
def test(color: str, alpha: str, merger: AlphaMerger):
    color_input_path = get_test_input_path(color)
    color_img = Image.open(color_input_path)
    alpha_input_file = get_test_input_path(alpha)
    alpha_img = Image.open(alpha_input_file)

    output_img = merger(color_img, alpha_img)

    if get_expected_output_mode(color_img) == "L":
        assert output_img.mode == "LA"
    else:
        assert output_img.mode == "RGBA"
    assert output_img.size == color_img.size
