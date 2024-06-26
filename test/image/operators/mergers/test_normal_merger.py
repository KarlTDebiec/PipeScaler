#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for NormalMerger"""
import pytest
from PIL import Image

from pipescaler.image.operators.mergers import NormalMerger
from pipescaler.image.testing import xfail_unsupported_image_mode
from pipescaler.testing.file import get_test_infile_path
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
def test(x: str, y: str, z: str, merger: NormalMerger) -> None:
    x_infile = get_test_infile_path(x)
    x_image = Image.open(x_infile)
    y_infile = get_test_infile_path(y)
    y_image = Image.open(y_infile)
    z_infile = get_test_infile_path(z)
    z_image = Image.open(z_infile)

    output_image = merger(x_image, y_image, z_image)

    assert output_image.mode == "RGB"
    assert output_image.size == x_image.size == y_image.size == z_image.size
