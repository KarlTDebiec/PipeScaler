#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for EsrganProcessor."""
import pytest
from PIL import Image

from pipescaler.image import get_expected_output_mode, xfail_unsupported_image_mode
from pipescaler.image.operators.processors import EsrganProcessor
from pipescaler.testing import (
    get_test_infile_path,
    get_test_model_infile_path,
    skip_if_ci,
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
    processor = EsrganProcessor(model_infile=get_test_model_infile_path(model))

    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
