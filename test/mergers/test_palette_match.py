#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for PaletteMatchMerger"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import PaletteMatchMode, get_palette, validate_image
from pipescaler.mergers import PaletteMatchMerger
from pipescaler.testing import (
    get_expected_output_mode,
    get_infile,
    parametrized_fixture,
    xfail_unsupported_image_mode,
)


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
    ("reference", "fit"),
    [
        # ("PL", "L"),
        # xfail_unsupported_image_mode()("PLA", "LA"),
        ("PRGB", "RGB"),
        # xfail_unsupported_image_mode()("PRGBA", "RGBA"),
    ],
)
def test(reference: str, fit: str, merger: PaletteMatchMerger):
    reference = get_infile(reference)
    fit = get_infile(fit)

    with temporary_filename(".png") as outfile:
        reference_image = validate_image(reference, ["L", "RGB"])
        fit_image = Image.open(fit)

        merger(reference=reference, fit=fit, outfile=outfile)

        with Image.open(outfile) as output_image:
            if get_expected_output_mode(fit_image) == "L":
                reference_colors = set(get_palette(reference_image))
                output_colors = set(get_palette(output_image))
            else:
                reference_colors = set(map(tuple, get_palette(reference_image)))
                output_colors = set(map(tuple, get_palette(output_image)))
            assert output_colors.issubset(reference_colors)
            assert output_image.mode == get_expected_output_mode(fit_image)
            assert output_image.size == fit_image.size
