#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PotraceProcessor."""

import pytest
from PIL import Image

from pipescaler.image.operators.processors import PotraceProcessor
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=PotraceProcessor,
    params=[
        {},
        {"scale": 2},
    ],
)
def processor(request) -> PotraceProcessor:
    return PotraceProcessor(**request.param)


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
def test(input_filename: str, processor: PotraceProcessor) -> None:
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.mode == "L"
    assert output_img.size == (
        input_img.size[0] * processor.scale,
        input_img.size[1] * processor.scale,
    )
