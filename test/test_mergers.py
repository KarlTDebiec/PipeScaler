#!/usr/bin/env python
#   test_mergers.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
""""""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import remove_palette_from_image
from pipescaler.mergers import (
    AlphaMerger,
    ColorMatchMerger,
    ColorToAlphaMerger,
    NormalMerger,
)
from shared import alt_infiles, infiles, xfail_unsupported_mode


@pytest.mark.parametrize(
    ("color", "alpha"),
    [
        (infiles["RGBA_color_RGB"], infiles["RGBA_alpha_L"]),
        (infiles["RGBA_color_PRGB"], infiles["RGBA_alpha_PL"]),
        (infiles["LA_color_L"], infiles["LA_alpha_L"]),
        (infiles["LA_color_PL"], infiles["LA_alpha_PL"]),
        xfail_unsupported_mode(infiles["RGBA"], infiles["L"]),
        xfail_unsupported_mode(infiles["RGB"], infiles["RGB"]),
        xfail_unsupported_mode(infiles["RGB"], infiles["RGBA"]),
    ],
)
def test_alpha_merger(color: str, alpha: str) -> None:
    with temporary_filename(".png") as outfile:
        color_image = Image.open(color)
        if color_image.mode == "P":
            color_image_mode = remove_palette_from_image(color_image).mode
        else:
            color_image_mode = color_image.mode
        alpha_image = Image.open(alpha)

        merger = AlphaMerger()
        merger(color=color, alpha=alpha, outfile=outfile)
        with Image.open(outfile) as output_image:
            if color_image_mode == "L":
                assert output_image.mode == "LA"
            else:
                assert output_image.mode == "RGBA"
            assert output_image.size == color_image.size


@pytest.mark.parametrize(
    ("reference", "target"),
    [
        (alt_infiles["L"], infiles["L"]),
        (alt_infiles["LA"], infiles["LA"]),
        (alt_infiles["RGB"], infiles["RGB"]),
        (alt_infiles["RGBA"], infiles["RGBA"]),
        (alt_infiles["PL"], infiles["PL"]),
        (alt_infiles["PLA"], infiles["PLA"]),
        (alt_infiles["PRGB"], infiles["PRGB"]),
        (alt_infiles["PRGBA"], infiles["PRGBA"]),
    ],
)
def test_color_match_merger(reference: str, target: str):
    with temporary_filename(".png") as outfile:
        reference_image = Image.open(reference)
        target_image = Image.open(target)
        if target_image.mode == "P":
            expected_output_mode = remove_palette_from_image(target_image).mode
        else:
            expected_output_mode = target_image.mode

        merger = ColorMatchMerger()
        merger(reference=reference, target=target, outfile=outfile)
        with Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode
            assert output_image.size == target_image.size


@pytest.mark.parametrize(
    ("color", "alpha"),
    [
        (infiles["RGB_magenta_color_RGB"], infiles["RGB_magenta_alpha_L"]),
        (infiles["RGB_magenta_color_PRGB"], infiles["RGB_magenta_alpha_PL"]),
        xfail_unsupported_mode(infiles["RGBA"], infiles["L"]),
        xfail_unsupported_mode(infiles["RGB"], infiles["RGB"]),
        xfail_unsupported_mode(infiles["RGB"], infiles["RGBA"]),
    ],
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
    [
        (
            infiles["RGB_normal_x_L"],
            infiles["RGB_normal_y_L"],
            infiles["RGB_normal_z_L"],
        ),
        (
            infiles["RGB_normal_x_PL"],
            infiles["RGB_normal_y_PL"],
            infiles["RGB_normal_z_PL"],
        ),
        xfail_unsupported_mode(infiles["RGB"], infiles["L"], infiles["L"]),
        xfail_unsupported_mode(infiles["L"], infiles["RGB"], infiles["L"]),
        xfail_unsupported_mode(infiles["L"], infiles["L"], infiles["RGB"]),
    ],
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
