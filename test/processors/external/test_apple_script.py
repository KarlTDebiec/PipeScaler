#!/usr/bin/env python
#   test/processors/external/test_apple_script.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for AppleScriptExternalProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import AppleScriptExternalProcessor
from pipescaler.testing import (
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
    xfail_if_platform,
)


@stage_fixture(
    cls=AppleScriptExternalProcessor,
    params=[
        {"script": "pixelmator/ml_super_resolution.scpt", "args": "2"},
    ],
)
def apple_script_external_processor(request) -> AppleScriptExternalProcessor:
    return AppleScriptExternalProcessor(**request.param)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile"),
    [
        xfail_if_platform({"Linux", "Windows"})("RGB"),
        xfail_if_platform({"Linux", "Windows"})("RGBA"),
    ],
)
def test(
    infile: str, apple_script_external_processor: AppleScriptExternalProcessor
) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        apple_script_external_processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size == (
                input_image.size[0] * int(apple_script_external_processor.args),
                input_image.size[1] * int(apple_script_external_processor.args),
            )


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        xfail_if_platform({"Linux", "Windows"}, raises=ValueError)(
            "RGB", "--script pixelmator/ml_super_resolution.scpt --args 2"
        ),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(AppleScriptExternalProcessor, args, infile)
