#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for SharpenProcessor."""
import pytest
from PIL import Image

from pipescaler.image.processors import SharpenProcessor
from pipescaler.testing import (
    get_expected_output_mode,
    get_infile,
    parametrized_fixture,
    xfail_unsupported_image_mode,
)


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
    infile = get_infile(infile)
    input_image = Image.open(infile)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
    assert output_image.size == input_image.size
