#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for NormalMerger"""

import pytest
from PIL import Image

from pipescaler.image.operators.mergers import NormalMerger
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=NormalMerger,
    params=[
        {},
    ],
)
def merger(request) -> NormalMerger:
    return NormalMerger(**request.param)


@pytest.mark.parametrize(
    ("x", "y", "z"),
    [
        ("split/RGB_normal_x_L", "split/RGB_normal_y_L", "split/RGB_normal_z_L"),
        xfail_unsupported_image_mode()("RGB", "L", "L"),
        xfail_unsupported_image_mode()("L", "RGB", "L"),
        xfail_unsupported_image_mode()("L", "L", "RGB"),
        ("split/RGB_normal_x_PL", "split/RGB_normal_y_PL", "split/RGB_normal_z_PL"),
    ],
)
def test(x: str, y: str, z: str, merger: NormalMerger):
    x_input_path = get_test_input_path(x)
    x_img = Image.open(x_input_path)
    y_input_path = get_test_input_path(y)
    y_img = Image.open(y_input_path)
    z_input_path = get_test_input_path(z)
    z_img = Image.open(z_input_path)

    output_img = merger(x_img, y_img, z_img)

    assert output_img.mode == "RGB"
    assert output_img.size == x_img.size == y_img.size == z_img.size
