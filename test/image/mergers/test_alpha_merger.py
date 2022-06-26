#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaMerger."""
import pytest
from PIL import Image

from pipescaler.image.mergers import AlphaMerger
from pipescaler.testing import (
    get_expected_output_mode,
    get_infile,
    parametrized_fixture,
    xfail_unsupported_image_mode,
)


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
def test(color: str, alpha: str, merger: AlphaMerger) -> None:
    color_infile = get_infile(color)
    color_image = Image.open(color_infile)
    alpha_infile = get_infile(alpha)
    alpha_image = Image.open(alpha_infile)

    output_image = merger(color_image, alpha_image)

    if get_expected_output_mode(color_image) == "L":
        assert output_image.mode == "LA"
    else:
        assert output_image.mode == "RGBA"
    assert output_image.size == color_image.size
