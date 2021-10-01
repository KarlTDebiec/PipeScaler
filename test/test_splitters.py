#!/usr/bin/env python
#   test_splitters.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import remove_palette_from_image
from pipescaler.splitters import AlphaSplitter, ColorToAlphaSplitter, NormalSplitter
from shared import infiles, xfail_unsupported_mode


@pytest.mark.parametrize(
    ("infile"),
    [
        (infiles["LA"]),
        (infiles["RGBA"]),
        (infiles["PLA"]),
        (infiles["PRGBA"]),
        xfail_unsupported_mode(infiles["L"]),
        xfail_unsupported_mode(infiles["RGB"]),
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
        (infiles["RGB_magenta"]),
        (infiles["RGB"]),
        (infiles["PRGB"]),
        xfail_unsupported_mode(infiles["L"]),
        xfail_unsupported_mode(infiles["LA"]),
        xfail_unsupported_mode(infiles["RGBA"]),
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
        (infiles["RGB_normal"]),
        (infiles["RGB"]),
        (infiles["PRGB"]),
        xfail_unsupported_mode(infiles["L"]),
        xfail_unsupported_mode(infiles["LA"]),
        xfail_unsupported_mode(infiles["RGBA"]),
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
