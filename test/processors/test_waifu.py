#!/usr/bin/env python
#   test/processors/test_waifu_external.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for WaifuProcessor"""
from os.path import dirname, join, normpath, sep, splitext

import pytest
from PIL import Image

from pipescaler.common import package_root, temporary_filename, validate_input_file
from pipescaler.processors import WaifuProcessor
from pipescaler.testing import (
    expected_output_mode,
    get_infile,
    skip_if_ci,
    stage_fixture,
    xfail_unsupported_image_mode,
)


def get_model_infile(name: str):
    base_directory = join(dirname(package_root), "test", "data", "models")
    split_name = normpath(name).split(sep)
    if len(split_name) == 1:
        sub_directory = "WaifuUpConv7"
    else:
        sub_directory = join(*split_name[:-1])
    filename = split_name[-1]
    if splitext(filename)[-1] == "":
        filename = f"{filename}.pth"

    return validate_input_file(join(base_directory, sub_directory, filename))


@stage_fixture(
    cls=WaifuProcessor,
    params=[
        {"model_infile": get_model_infile("WaifuUpConv7/a-2-3")},
        {"model_infile": get_model_infile("WaifuVgg7/a-1-3")},
    ],
)
def waifu_processor(request) -> WaifuProcessor:
    return WaifuProcessor(**request.param)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile"),
    [
        skip_if_ci(xfail_unsupported_image_mode())("1"),
        skip_if_ci()("L"),
        skip_if_ci(xfail_unsupported_image_mode())("LA"),
        skip_if_ci()("RGB"),
        skip_if_ci(xfail_unsupported_image_mode())("RGBA"),
    ],
)
def test(infile: str, waifu_processor: WaifuProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        waifu_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)
