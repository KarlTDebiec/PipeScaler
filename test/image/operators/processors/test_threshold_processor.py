#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ThresholdProcessor."""

import numpy as np
import pytest
from PIL import Image

from pipescaler.image.operators.processors import ThresholdProcessor
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=ThresholdProcessor,
    params=[
        {"threshold": 128, "denoise": False},
        {"threshold": 128, "denoise": True},
    ],
)
def processor(request) -> ThresholdProcessor:
    return ThresholdProcessor(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        "1",
        "L",
        xfail_unsupported_image_mode()("LA"),
        xfail_unsupported_image_mode()("RGB"),
        xfail_unsupported_image_mode()("RGBA"),
        "PL",
        xfail_unsupported_image_mode()("PLA"),
        xfail_unsupported_image_mode()("PRGB"),
        xfail_unsupported_image_mode()("PRGBA"),
    ],
)
def test(input_filename: str, processor: ThresholdProcessor) -> None:
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    output_arr = np.array(output_img)
    assert output_img.size == input_img.size
    if input_img.mode == "1":
        assert output_img.mode == "1"
    else:
        assert output_img.mode == "L"
        assert np.logical_or(output_arr == 0, output_arr == 255).all()
