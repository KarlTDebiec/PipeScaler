#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for HistogramMatchMerger"""
import pytest
from PIL import Image

from pipescaler.image.operators.mergers import HistogramMatchMerger
from pipescaler.image.testing import get_expected_output_mode
from pipescaler.testing.file import get_test_infile_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=HistogramMatchMerger,
    params=[
        {},
    ],
)
def merger(request) -> HistogramMatchMerger:
    return HistogramMatchMerger(**request.param)


@pytest.mark.parametrize(
    ("ref", "fit"),
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
def test(ref: str, fit: str, merger: HistogramMatchMerger):
    ref_infile = get_test_infile_path(ref)
    ref_image = Image.open(ref_infile)
    fit_infile = get_test_infile_path(fit)
    fit_image = Image.open(fit_infile)

    output_image = merger(ref_image, fit_image)

    assert output_image.mode == get_expected_output_mode(fit_image)
    assert output_image.size == fit_image.size
