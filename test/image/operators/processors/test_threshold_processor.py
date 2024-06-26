#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ThresholdProcessor."""
import numpy as np
import pytest
from PIL import Image

from pipescaler.image.operators.processors import ThresholdProcessor
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_infile_path
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
    "infile",
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
def test(infile: str, processor: ThresholdProcessor) -> None:
    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    output_image = processor(input_image)

    output_datum = np.array(output_image)
    assert output_image.size == input_image.size
    if input_image.mode == "1":
        assert output_image.mode == "1"
    else:
        assert output_image.mode == "L"
        assert np.logical_or(output_datum == 0, output_datum == 255).all()
