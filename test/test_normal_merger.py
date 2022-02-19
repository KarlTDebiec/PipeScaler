#!/usr/bin/env python
#   test_normal_merger.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
import pytest
from PIL import Image
from shared import get_infile, xfail_unsupported_mode

from pipescaler.common import temporary_filename
from pipescaler.mergers import NormalMerger


@pytest.fixture()
def normal_merger(request) -> NormalMerger:
    return NormalMerger(**request.param)


@pytest.mark.parametrize(
    ("x", "y", "z", "normal_merger"),
    [
        ("split/RGB_normal_x_L", "split/RGB_normal_y_L", "split/RGB_normal_z_L", {}),
        xfail_unsupported_mode()("RGB", "L", "L", {}),
        xfail_unsupported_mode()("L", "RGB", "L", {}),
        xfail_unsupported_mode()("L", "L", "RGB", {}),
        ("split/RGB_normal_x_PL", "split/RGB_normal_y_PL", "split/RGB_normal_z_PL", {}),
    ],
    indirect=["normal_merger"],
)
def test_normal_merger(x: str, y: str, z: str, normal_merger: NormalMerger) -> None:
    x = get_infile(x)
    y = get_infile(y)
    z = get_infile(z)

    with temporary_filename(".png") as outfile:
        x_image = Image.open(x)
        y_image = Image.open(y)
        z_image = Image.open(z)

        normal_merger(x=x, y=y, z=z, outfile=outfile)

        with Image.open(outfile) as output_image:
            assert output_image.mode == "RGB"
            assert output_image.size == x_image.size == y_image.size == z_image.size
