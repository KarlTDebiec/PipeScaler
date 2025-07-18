#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ModeProcessor."""

import pytest
from PIL import Image

from pipescaler.image.operators.processors import ModeProcessor
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=ModeProcessor,
    params=[
        {"mode": "1"},
        {"mode": "L"},
        {"mode": "LA"},
        {"mode": "RGB"},
        {"mode": "RGBA"},
    ],
)
def processor(request) -> ModeProcessor:
    return ModeProcessor(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        "1",
        "L",
        "LA",
        "RGB",
        "RGBA",
        "PL",
        "PLA",
        "PRGB",
        "PRGBA",
    ],
)
def test(input_filename: str, processor: ModeProcessor) -> None:
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.size == input_img.size
    assert output_img.mode == processor.mode
