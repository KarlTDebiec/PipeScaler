#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for XbrzProcessor."""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors.image import XbrzProcessor
from pipescaler.testing import expected_output_mode, get_infile, parametrized_fixture


@parametrized_fixture(
    cls=XbrzProcessor,
    params=[
        {"scale": 2},
    ],
)
def processor(request) -> XbrzProcessor:
    return XbrzProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
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
def test(infile: str, processor: XbrzProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
            assert output_image.size == (
                input_image.size[0] * processor.scale,
                input_image.size[1] * processor.scale,
            )
