#!/usr/bin/env python
#   test_splitters.py
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
from pipescaler.core import UnsupportedImageModeError, remove_palette_from_image
from pipescaler.splitters import AlphaSplitter, ColorToAlphaSplitter, NormalSplitter

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
        "RGBA.png",
    ]
}
xfail = pytest.mark.xfail

####################################### FIXTURES #######################################
@pytest.fixture(params=infiles.keys())
def infile(request):
    return infiles[request.param]


######################################## TESTS #########################################
@pytest.mark.parametrize(
    ("infile"),
    [
        pytest.param(infiles["L"], marks=xfail(raises=UnsupportedImageModeError)),
        (infiles["LA"]),
        pytest.param(infiles["P_L"], marks=xfail(raises=UnsupportedImageModeError)),
        (infiles["P_LA"]),
        pytest.param(infiles["P_RGB"], marks=xfail(raises=UnsupportedImageModeError)),
        (infiles["P_RGBA"]),
        pytest.param(infiles["RGB"], marks=xfail(raises=UnsupportedImageModeError)),
        (infiles["RGBA"]),
    ],
)
def test_alpha_splitter(infile: str) -> None:
    with temporary_filename(".png") as color_outfile:
        with temporary_filename(".png") as alpha_outfile:
            input_image = Image.open(infile)
            if input_image.mode == "P":
                expected_color_mode = remove_palette_from_image(
                    input_image
                ).mode.rstrip("A")
            else:
                expected_color_mode = input_image.mode.rstrip("A")

            splitter = AlphaSplitter()
            splitter(infile, color=color_outfile, alpha=alpha_outfile)

            with Image.open(color_outfile) as color_image:
                assert color_image.mode == expected_color_mode
                assert color_image.size == input_image.size

            with Image.open(alpha_outfile) as alpha_image:
                assert alpha_image.mode == "L"
                assert alpha_image.size == input_image.size


@pytest.mark.parametrize(
    ("infile"),
    [
        pytest.param(infiles["L"], marks=xfail(raises=UnsupportedImageModeError)),
        pytest.param(infiles["LA"], marks=xfail(raises=UnsupportedImageModeError)),
        pytest.param(infiles["P_L"], marks=xfail(raises=UnsupportedImageModeError)),
        pytest.param(infiles["P_LA"], marks=xfail(raises=UnsupportedImageModeError)),
        (infiles["P_RGB"]),
        pytest.param(infiles["P_RGBA"], marks=xfail(raises=UnsupportedImageModeError)),
        (infiles["RGB"]),
        (infiles["RGB_MAGENTA"]),
        pytest.param(infiles["RGBA"], marks=xfail(raises=UnsupportedImageModeError)),
    ],
)
def test_color_to_alpha_splitter(infile: str) -> None:
    with temporary_filename(".png") as color_outfile:
        with temporary_filename(".png") as alpha_outfile:
            input_image = Image.open(infile)

            splitter = ColorToAlphaSplitter(alpha_color=[255, 0, 255])
            splitter(infile, color=color_outfile, alpha=alpha_outfile)

            with Image.open(color_outfile) as color_image:
                assert color_image.mode == "RGB"
                assert color_image.size == input_image.size

            with Image.open(alpha_outfile) as alpha_image:
                assert alpha_image.mode == "L"
                assert alpha_image.size == input_image.size


@pytest.mark.parametrize(
    ("infile"),
    [
        pytest.param(infiles["L"], marks=xfail(raises=UnsupportedImageModeError)),
        pytest.param(infiles["LA"], marks=xfail(raises=UnsupportedImageModeError)),
        pytest.param(infiles["P_L"], marks=xfail(raises=UnsupportedImageModeError)),
        pytest.param(infiles["P_LA"], marks=xfail(raises=UnsupportedImageModeError)),
        (infiles["P_RGB"]),
        pytest.param(infiles["P_RGBA"], marks=xfail(raises=UnsupportedImageModeError)),
        (infiles["RGB"]),
        (infiles["RGB_NORMAL"]),
        pytest.param(infiles["RGBA"], marks=xfail(raises=UnsupportedImageModeError)),
    ],
)
def test_normal_splitter(infile: str) -> None:
    with temporary_filename(".png") as x_outfile:
        with temporary_filename(".png") as y_outfile:
            with temporary_filename(".png") as z_outfile:
                input_image = Image.open(infile)

                splitter = NormalSplitter()
                splitter(infile, x=x_outfile, y=y_outfile, z=z_outfile)

                with Image.open(x_outfile) as x_image:
                    assert x_image.mode == "L"
                    assert x_image.size == input_image.size

                with Image.open(y_outfile) as y_image:
                    assert y_image.mode == "L"
                    assert y_image.size == input_image.size

                with Image.open(z_outfile) as z_image:
                    assert z_image.mode == "L"
                    assert z_image.size == input_image.size
