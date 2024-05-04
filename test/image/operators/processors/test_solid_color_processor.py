#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SolidColorProcessor."""
import pytest
from PIL import Image

from pipescaler.image import get_expected_output_mode
from pipescaler.image.operators.processors import SolidColorProcessor
from pipescaler.testing import get_test_infile_path, parametrized_fixture


@parametrized_fixture(
    cls=SolidColorProcessor,
    params=[
        {},
    ],
)
def processor(request) -> SolidColorProcessor:
    return SolidColorProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        ("1"),
        ("L"),
        ("LA"),
        ("RGB"),
        ("RGBA"),
        ("PL"),
        ("PLA"),
        ("PRGB"),
        ("PRGBA"),
    ],
)
def test(infile: str, processor: SolidColorProcessor) -> None:
    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
    assert output_image.size == input_image.size
    assert len(output_image.getcolors()) == 1
