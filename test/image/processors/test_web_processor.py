#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for WebProcessor."""
from multiprocessing import Process
from time import sleep

from PIL import Image
from pytest import mark

from pipescaler.image.processors import WebProcessor, XbrzProcessor
from pipescaler.testing import get_infile, parametrized_fixture
from pipescaler.utilities import Host


@parametrized_fixture(
    cls=XbrzProcessor,
    params=[
        {"scale": 2},
    ],
)
def xbrz_processor(request) -> XbrzProcessor:
    return XbrzProcessor(**request.param)


@parametrized_fixture(
    cls=WebProcessor,
    params=[
        {"url": "http://127.0.0.1:5000/xbrz-2"},
    ],
)
def web_processor(request) -> WebProcessor:
    return WebProcessor(**request.param)


@mark.parametrize(
    ("infile"),
    [
        ("RGB"),
    ],
)
def test(infile: str, web_processor: WebProcessor, xbrz_processor: XbrzProcessor):
    infile = get_infile(infile)
    input_image = Image.open(infile)

    host = Host(processors={"xbrz-2": xbrz_processor})
    process = Process(target=host.__call__)
    process.start()
    sleep(5)
    output_image = web_processor(input_image)
    process.kill()
    assert output_image.size == (
        input_image.size[0] * xbrz_processor.scale,
        input_image.size[1] * xbrz_processor.scale,
    )
