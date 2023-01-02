#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for PaletteMatchMerger"""
import pytest
from PIL import Image

from pipescaler.image import get_expected_output_mode
from pipescaler.image.core import get_palette, remove_palette
from pipescaler.image.core.enums import PaletteMatchMode
from pipescaler.image.operators.mergers import PaletteMatchMerger
from pipescaler.testing import get_test_infile_path, parametrized_fixture


@parametrized_fixture(
    cls=PaletteMatchMerger,
    params=[
        {"palette_match_mode": PaletteMatchMode.BASIC},
        {"palette_match_mode": PaletteMatchMode.LOCAL},
    ],
)
def merger(request) -> PaletteMatchMerger:
    return PaletteMatchMerger(**request.param)


@pytest.mark.parametrize(
    ("ref", "fit"),
    [
        ("PL", "L"),
        # xfail_unsupported_image_mode()("PLA", "LA"),
        # ("PRGB", "RGB"),
        # xfail_unsupported_image_mode()("PRGBA", "RGBA"),
    ],
)
def test(ref: str, fit: str, merger: PaletteMatchMerger):
    ref_infile = get_test_infile_path(ref)
    ref_image = Image.open(ref_infile)
    fit_infile = get_test_infile_path(fit)
    fit_image = Image.open(fit_infile)

    output_image = merger(ref_image, fit_image)

    if get_expected_output_mode(fit_image) == "L":
        ref_colors = set(get_palette(remove_palette(ref_image)))
        output_colors = set(get_palette(output_image))
    else:
        ref_colors = set(map(tuple, get_palette(remove_palette(ref_image))))
        output_colors = set(map(tuple, get_palette(output_image)))
    assert output_colors.issubset(ref_colors)
    assert output_image.mode == get_expected_output_mode(fit_image)
    assert output_image.size == fit_image.size
