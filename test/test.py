#!/usr/bin/env python
#   test.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from os import getcwd, remove
from os.path import join
from sys import platform
from tempfile import NamedTemporaryFile

import pytest

from pipescaler.processors import (ESRGANProcessor, Pixelmator2xProcessor,
                                   PotraceProcessor, ThresholdProcessor,
                                   WaifuPixelmator2xTransparentProcessor,
                                   WaifuProcessor)


################################## FIXTURES ###################################
@pytest.fixture(params=[ESRGANProcessor, Pixelmator2xProcessor,
                        PotraceProcessor, ThresholdProcessor,
                        WaifuPixelmator2xTransparentProcessor,
                        WaifuProcessor])
def cl_processor(request):
    return request.param


@pytest.fixture(params=["1x_BC1-smooth2.pth", "RRDB_ESRGAN_x4.pth",
                        "RRDB_ESRGAN_x4_old_arch.pth"])
def esrgan_model(request):
    return join(getcwd(), "models", request.param)


@pytest.fixture
def rgb():
    return join(getcwd(), "data", "1x", "rgb.png")


#################################### TESTS ####################################
def test_construct_argparser(cl_processor):
    cl_processor.construct_argparser()


def test_esrgan(rgb, esrgan_model):
    outfile = NamedTemporaryFile(delete=False, suffix=".png")
    outfile.close()
    ESRGANProcessor.process_file_from_cl(rgb, outfile.name,
                                         esrgan_model, verbosity=2)
    remove(outfile.name)


def test_potrace(rgb):
    outfile = NamedTemporaryFile(delete=False, suffix=".png")
    outfile.close()
    PotraceProcessor.process_file_from_cl(rgb, outfile.name,
                                          verbosity=2)
    remove(outfile.name)


@pytest.mark.skipif(platform != "darwin",
                    reason="Application only available on macOS")
def test_pixelmator(rgb):
    outfile = NamedTemporaryFile(delete=False, suffix=".png")
    outfile.close()
    Pixelmator2xProcessor.process_file_from_cl(rgb, outfile.name,
                                               verbosity=2)
    remove(outfile.name)
