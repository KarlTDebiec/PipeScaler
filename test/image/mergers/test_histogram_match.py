#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for HistogramMatchMerger"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import remove_palette_from_image
from pipescaler.image.mergers import HistogramMatchMerger
from pipescaler.testing import get_infile, parametrized_fixture


@parametrized_fixture(cls=HistogramMatchMerger, params=[{}])
def merger(request) -> HistogramMatchMerger:
    return HistogramMatchMerger(**request.param)


@pytest.mark.parametrize(
    ("reference", "fit"),
    [
        ("alt/L", "L"),
        ("alt/LA", "LA"),
        ("alt/RGB", "RGB"),
        ("alt/RGBA", "RGBA"),
        ("alt/PL", "PL"),
        ("alt/PLA", "PLA"),
        ("alt/PRGB", "PRGB"),
        ("alt/PRGBA", "PRGBA"),
    ],
)
def test(reference: str, fit: str, merger: HistogramMatchMerger):
    reference = get_infile(reference)
    fit = get_infile(fit)

    with temporary_filename(".png") as outfile:
        fit_image = Image.open(fit)
        if fit_image.mode == "P":
            expected_output_mode = remove_palette_from_image(fit_image).mode
        else:
            expected_output_mode = fit_image.mode

        merger(reference=reference, fit=fit, outfile=outfile)

        with Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode
            assert output_image.size == fit_image.size
