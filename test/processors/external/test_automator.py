#!/usr/bin/env python
#   test/processors/external/test_automator.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for AutomatorProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import AutomatorProcessor
from pipescaler.testing import (
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
    xfail_if_platform,
)


@stage_fixture(
    cls=AutomatorProcessor,
    params=[
        {"workflow": "pixelmator/denoise.workflow"},
    ],
)
def processor(request) -> AutomatorProcessor:
    return AutomatorProcessor(**request.param)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile"),
    [
        xfail_if_platform({"Linux", "Windows"})("RGB"),
        xfail_if_platform({"Linux", "Windows"})("RGBA"),
    ],
)
def test(infile: str, processor: AutomatorProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        processor(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode == input_image.mode
            assert output_image.size == input_image.size


@pytest.mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        xfail_if_platform({"Linux", "Windows"}, raises=ValueError)(
            "RGB", "--workflow pixelmator/denoise.workflow"
        ),
    ],
)
def test_cl(infile: str, args: str) -> None:
    infile = get_infile(infile)

    run_processor_on_command_line(AutomatorProcessor, args, infile)
