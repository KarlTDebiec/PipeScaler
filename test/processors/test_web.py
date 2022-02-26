#!/usr/bin/env python
#   test/processors/test_web.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for WebProcessor"""
from inspect import getfile
from signal import SIGTERM
from subprocess import PIPE, Popen

import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.processors import WebProcessor
from pipescaler.scripts.pipescaler_host import PipescalerHost
from pipescaler.testing import expected_output_mode, get_infile, stage_fixture


@pytest.fixture()
def conf():
    return """
stages:
    xbrz-2:
        XbrzProcessor:
            scale: 2
"""


@stage_fixture(
    cls=WebProcessor,
    params=[
        {"url": "http://127.0.0.1:5000/xbrz-2"},
    ],
)
def web_processor(request) -> WebProcessor:
    return WebProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        ("RGB"),
    ],
)
def test(conf: str, infile: str, web_processor: WebProcessor):
    infile = get_infile(infile)

    with temporary_filename(".yml") as conf_outfile_name:
        with open(conf_outfile_name, "w") as conf_outfile:
            conf_outfile.write(conf)

        command = f"coverage run {getfile(PipescalerHost)} {conf_outfile_name}"
        with Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as child:
            child.stderr.readline()
            with temporary_filename(".png") as outfile:
                web_processor(infile, outfile)

                child.send_signal(SIGTERM)

                with Image.open(infile) as input_image, Image.open(
                    outfile
                ) as output_image:
                    assert output_image.mode == expected_output_mode(input_image)