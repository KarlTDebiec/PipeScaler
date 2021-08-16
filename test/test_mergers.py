#!/usr/bin/env python
#   test_merges.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
####################################### MODULES ########################################
from os import getcwd
from os.path import join

import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import remove_palette_from_image
from pipescaler.mergers import AlphaMerger, ColorToAlphaMerger, NormalMerger
from pipescaler.splitters import AlphaSplitter

###################################### VARIABLES #######################################
infiles = {
    f[:-4].upper(): join(getcwd(), "data", "infiles", f)
    for f in [
        "L.png",
        "LA.png",
        "P_L.png",
        "P_LA.png",
        "P_RGB.png",
        "P_RGBA.png",
        "RGB.png",
        "RGB_magenta.png",
        "RGB_magenta_alpha.png",
        "RGB_magenta_color.png",
        "RGB_normal.png",
        "RGB_normal_x.png",
        "RGB_normal_y.png",
        "RGB_normal_z.png",
        "RGBA.png",
        "RGBA_color.png",
        "RGBA_alpha.png",
    ]
}


######################################## TESTS #########################################
@pytest.mark.parametrize(
    ("color", "alpha"), [(infiles["RGBA_COLOR"], infiles["RGBA_ALPHA"])]
)
def test_alpha_merger(color: str, alpha: str) -> None:
    with temporary_filename(".png") as outfile:
        color_image = Image.open(color)
        alpha_image = Image.open(alpha)

        merger = AlphaMerger()
        merger(color=color, alpha=alpha, outfile=outfile)
        with Image.open(outfile) as output_image:
            assert output_image.mode == "RGBA"
            assert output_image.size == color_image.size


@pytest.mark.parametrize(
    ("color", "alpha"), [(infiles["RGB_MAGENTA_COLOR"], infiles["RGB_MAGENTA_ALPHA"])]
)
def test_color_to_alpha_merger(color: str, alpha: str) -> None:
    with temporary_filename(".png") as outfile:
        color_image = Image.open(color)
        alpha_image = Image.open(alpha)

        merger = ColorToAlphaMerger(alpha_color=[255, 0, 255])
        merger(color=color, alpha=alpha, outfile=outfile)
        with Image.open(outfile) as output_image:
            assert output_image.mode == "RGB"
            assert output_image.size == color_image.size


@pytest.mark.parametrize(
    ("x", "y", "z"),
    [(infiles["RGB_NORMAL_X"], infiles["RGB_NORMAL_Y"], infiles["RGB_NORMAL_Z"])],
)
def test_normal_merger(x: str, y: str, z: str) -> None:
    with temporary_filename(".png") as outfile:
        x_image = Image.open(x)
        y_image = Image.open(y)
        z_image = Image.open(z)

        merger = NormalMerger()
        merger(x=x, y=y, z=z, outfile=outfile)
        with Image.open(outfile) as output_image:
            assert output_image.mode == "RGB"
            assert output_image.size == x_image.size
