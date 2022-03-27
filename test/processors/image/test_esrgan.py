#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for ESRGANProcessor."""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import ESRGANProcessor
from pipescaler.testing import (
    expected_output_mode,
    get_infile,
    get_model_infile,
    skip_if_ci,
    stage_fixture,
    xfail_unsupported_image_mode,
)


@stage_fixture(
    cls=ESRGANProcessor,
    params=[
        {"model_infile": get_model_infile("ESRGAN/1x_BC1-smooth2")},
        {"model_infile": get_model_infile("ESRGAN/RRDB_ESRGAN_x4")},
        {"model_infile": get_model_infile("ESRGAN/RRDB_ESRGAN_x4_old_arch")},
    ],
)
def processor(request) -> ESRGANProcessor:
    return ESRGANProcessor(**request.param)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile"),
    [
        skip_if_ci()("1"),
        skip_if_ci()("L"),
        skip_if_ci(xfail_unsupported_image_mode())("LA"),
        skip_if_ci(xfail_unsupported_image_mode())("RGBA"),
        skip_if_ci()("RGB"),
        skip_if_ci()("PL"),
        skip_if_ci(xfail_unsupported_image_mode())("PLA"),
        skip_if_ci()("PRGB"),
        skip_if_ci(xfail_unsupported_image_mode())("PRGBA"),
    ],
)
def test(infile: str, processor: ESRGANProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
