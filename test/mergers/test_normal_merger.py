#!/usr/bin/env python
#   test/mergers/test_normal_merger.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for NormalMerger"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.mergers import NormalMerger
from pipescaler.testing import get_infile, stage_fixture, xfail_unsupported_image_mode


@stage_fixture(cls=NormalMerger, params=[{}])
def normal_merger(request) -> NormalMerger:
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
def test(x: str, y: str, z: str, normal_merger: NormalMerger) -> None:
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
