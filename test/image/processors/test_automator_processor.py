#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for AutomatorProcessor"""
import pytest
from PIL import Image

from pipescaler.image.processors.automator_processor import AutomatorProcessor
from pipescaler.testing import (
    get_infile,
    parametrized_fixture,
    skip_if_ci,
    xfail_if_platform,
)


@parametrized_fixture(
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
        skip_if_ci(xfail_if_platform({"Linux", "Windows"}))("RGB"),
    ],
)
def test(infile: str, processor: AutomatorProcessor) -> None:
    infile = get_infile(infile)
    input_image = Image.open(infile)
    output_image = processor(input_image)

    assert output_image.mode == input_image.mode
    assert output_image.size == input_image.size
