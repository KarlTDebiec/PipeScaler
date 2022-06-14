#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for CropProcessor."""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.image.processors import CropProcessor
from pipescaler.testing import (
    get_expected_output_mode,
    get_infile,
    parametrized_fixture,
)


@parametrized_fixture(
    cls=CropProcessor,
    params=[
        {"pixels": (4, 4, 4, 4)},
    ],
)
def processor(request) -> CropProcessor:
    return CropProcessor(**request.param)


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
def test(infile: str, processor: CropProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == get_expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] - processor.left - processor.right,
                input_image.size[1] - processor.top - processor.bottom,
            )
