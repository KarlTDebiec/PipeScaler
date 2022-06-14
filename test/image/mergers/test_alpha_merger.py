#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for AlphaMerger."""
import pytest
from PIL import Image

from pipescaler.core.image import remove_palette
from pipescaler.image.mergers import AlphaMerger
from pipescaler.testing import (
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

    if color_image.mode == "P":
        color_image_mode = remove_palette(color_image).mode
    else:
        color_image_mode = color_image.mode

    output_image = merger(color_image, alpha_image)
    if color_image_mode == "L":
        assert output_image.mode == "LA"
    else:
        assert output_image.mode == "RGBA"
    assert output_image.size == color_image.size
