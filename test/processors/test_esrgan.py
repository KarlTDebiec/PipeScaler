#!/usr/bin/env python
#   test/processors/test_esrgan.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for ESRGANProcessor"""
from os.path import dirname, join, normpath, sep, splitext

import pytest
from PIL import Image

from pipescaler.common import package_root, temporary_filename, validate_input_file
from pipescaler.processors import ESRGANProcessor
from pipescaler.testing import (
    expected_output_mode,
    get_infile,
    run_processor_on_command_line,
    skip_if_ci,
    stage_fixture,
    xfail_unsupported_image_mode,
)


def get_model_infile(name: str):
    base_directory = join(dirname(package_root), "test", "data", "models")
    split_name = normpath(name).split(sep)
    if len(split_name) == 1:
        sub_directory = "ESRGAN"
    else:
        sub_directory = join(*split_name[:-1])
    filename = split_name[-1]
    if splitext(filename)[-1] == "":
        filename = f"{filename}.pth"

    return validate_input_file(join(base_directory, sub_directory, filename))


@stage_fixture(
    cls=ESRGANProcessor,
    params=[
        {"model_infile": get_model_infile("1x_BC1-smooth2")},
        {"model_infile": get_model_infile("RRDB_ESRGAN_x4")},
        {"model_infile": get_model_infile("RRDB_ESRGAN_x4_old_arch")},
    ],
)
def esrgan_processor(request) -> ESRGANProcessor:
    return ESRGANProcessor(**request.param)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile"),
    [
        skip_if_ci()("1"),
        skip_if_ci()("L"),
        skip_if_ci(xfail_unsupported_image_mode())("LA"),
        skip_if_ci(xfail_unsupported_image_mode())("RGBA"),
        skip_if_ci()("RGB"),
        skip_if_ci()("PL"),
        skip_if_ci(xfail_unsupported_image_mode())("PLA"),
        skip_if_ci()("PRGB"),
        skip_if_ci(xfail_unsupported_image_mode())("PRGBA"),
    ],
)
def test(infile: str, esrgan_processor: ESRGANProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        esrgan_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == expected_output_mode(input_image)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        skip_if_ci()("RGB", f"--model {get_model_infile('1x_BC1-smooth2')}"),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(ESRGANProcessor, args, infile)
