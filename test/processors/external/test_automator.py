#!/usr/bin/env python
#   test/processors/external/test_automator.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for AutomatorExternalProcessor"""
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import AutomatorExternalProcessor
from pipescaler.testing import (
    get_infile,
    run_processor_on_command_line,
    stage_fixture,
    xfail_if_platform,
)


@stage_fixture(
    cls=AutomatorExternalProcessor,
    params=[
        {"workflow": "pixelmator/denoise.workflow"},
    ],
)
def automator_external_processor(request) -> AutomatorExternalProcessor:
    return AutomatorExternalProcessor(**request.param)


@pytest.mark.serial
@pytest.mark.parametrize(
    ("infile"),
    [
        xfail_if_platform({"Linux", "Windows"})("RGB"),
        xfail_if_platform({"Linux", "Windows"})("RGBA"),
    ],
)
def test(infile: str, automator_external_processor: AutomatorExternalProcessor) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        automator_external_processor(infile, outfile)

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

    run_processor_on_command_line(AutomatorExternalProcessor, args, infile)
