#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuProcessor."""

import pytest
from PIL import Image

from pipescaler.image.operators.processors import WaifuProcessor
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)
from pipescaler.testing.file import get_test_input_path, get_test_model_path
from pipescaler.testing.mark import skip_if_ci, skip_if_codex


@pytest.mark.serial
@pytest.mark.parametrize(
    ("input_filename", "model"),
    [
        skip_if_codex(skip_if_ci(xfail_unsupported_image_mode()))(
            "1", "WaifuUpConv7/a-2-3"
        ),
        skip_if_codex(skip_if_ci())("L", "WaifuUpConv7/a-2-3"),
        skip_if_codex(skip_if_ci(xfail_unsupported_image_mode()))(
            "LA", "WaifuUpConv7/a-2-3"
        ),
        skip_if_codex(skip_if_ci())("RGB", "WaifuUpConv7/a-2-3"),
        skip_if_codex(skip_if_ci())("RGB", "WaifuVgg7/a-1-3"),
        skip_if_codex(skip_if_ci(xfail_unsupported_image_mode()))(
            "RGBA", "WaifuUpConv7/a-2-3"
        ),
    ],
)
def test(input_filename: str, model: str):
    processor = WaifuProcessor(model_input_path=get_test_model_path(model))

    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.mode == get_expected_output_mode(input_img)
