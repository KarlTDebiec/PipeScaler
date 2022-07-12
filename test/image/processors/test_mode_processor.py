#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for ModeProcessor."""
import pytest
from PIL import Image

from pipescaler.image.processors import ModeProcessor
from pipescaler.testing import get_test_infile_path, parametrized_fixture


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
def test(infile: str, processor: ModeProcessor) -> None:
    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    output_image = processor(input_image)

    assert output_image.size == input_image.size
    assert output_image.mode == processor.mode
