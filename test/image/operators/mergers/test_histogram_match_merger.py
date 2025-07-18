#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for HistogramMatchMerger"""

import pytest
from PIL import Image

from pipescaler.image.operators.mergers import HistogramMatchMerger
from pipescaler.image.testing import get_expected_output_mode
from pipescaler.testing.file import get_test_input_path
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
    ref_input_path = get_test_input_path(ref)
    ref_img = Image.open(ref_input_path)
    fit_input_path = get_test_input_path(fit)
    fit_img = Image.open(fit_input_path)

    output_img = merger(ref_img, fit_img)

    assert output_img.mode == get_expected_output_mode(fit_img)
    assert output_img.size == fit_img.size
