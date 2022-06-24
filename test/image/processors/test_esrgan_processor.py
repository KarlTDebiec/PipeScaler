#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for EsrganProcessor."""
import pytest
from PIL import Image

from pipescaler.image.processors import EsrganProcessor
from pipescaler.testing import (
    get_expected_output_mode,
    get_infile,
    get_model_infile,
    parametrized_fixture,
    skip_if_ci,
    xfail_unsupported_image_mode,
)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile", "model"),
    [
        skip_if_ci()("1", "ESRGAN/1x_BC1-smooth2"),
        skip_if_ci()("L", "ESRGAN/1x_BC1-smooth2"),
        skip_if_ci(xfail_unsupported_image_mode())("LA", "ESRGAN/1x_BC1-smooth2"),
        skip_if_ci(xfail_unsupported_image_mode())("RGBA", "ESRGAN/1x_BC1-smooth2"),
        skip_if_ci()("RGB", "ESRGAN/1x_BC1-smooth2"),
        skip_if_ci()("RGB", "ESRGAN/1x_BC1-smooth2_out"),
        skip_if_ci()("RGB", "ESRGAN/RRDB_ESRGAN_x4"),
        skip_if_ci()("RGB", "ESRGAN/RRDB_ESRGAN_x4_out"),
        skip_if_ci()("RGB", "ESRGAN/1x_BC1-smooth2_out"),
        skip_if_ci()("RGB", "ESRGAN/RRDB_ESRGAN_x4_old_arch"),
        skip_if_ci()("RGB", "ESRGAN/RRDB_ESRGAN_x4_old_arch_out"),
        skip_if_ci()("PL", "ESRGAN/1x_BC1-smooth2"),
        skip_if_ci(xfail_unsupported_image_mode())("PLA", "ESRGAN/1x_BC1-smooth2"),
        skip_if_ci()("PRGB", "ESRGAN/1x_BC1-smooth2"),
        skip_if_ci(xfail_unsupported_image_mode())("PRGBA", "ESRGAN/1x_BC1-smooth2"),
    ],
)
def test(infile: str, model: str) -> None:
    processor = EsrganProcessor(model_infile=get_model_infile(model))

    infile = get_infile(infile)
    input_image = Image.open(infile)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
