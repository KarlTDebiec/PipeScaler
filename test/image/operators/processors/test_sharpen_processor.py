#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SharpenProcessor."""
import pytest
from PIL import Image

from pipescaler.image import get_expected_output_mode, xfail_unsupported_image_mode
from pipescaler.image.operators.processors import SharpenProcessor
from pipescaler.testing import get_test_infile_path, parametrized_fixture


@parametrized_fixture(
    cls=SharpenProcessor,
    params=[
        {},
    ],
)
def processor(request) -> SharpenProcessor:
    return SharpenProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        xfail_unsupported_image_mode()("1"),
        ("L"),
        xfail_unsupported_image_mode()("LA"),
        ("RGB"),
        xfail_unsupported_image_mode()("RGBA"),
        ("PL"),
        xfail_unsupported_image_mode()("PLA"),
        ("PRGB"),
        xfail_unsupported_image_mode()("PRGBA"),
    ],
)
def test(infile: str, processor: SharpenProcessor) -> None:
    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
    assert output_image.size == input_image.size
