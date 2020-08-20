#!/usr/bin/env python
#   test.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from os import getcwd
from os.path import join

import pytest
from PIL import Image

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


@pytest.fixture
def dabenxiang():
    return join(getcwd(), "data", "1x", "dabenxiang.png")


#################################### TESTS ####################################
def test_construct_argparser(cl_processor):
    cl_processor.construct_argparser()


def test_potrace(dabenxiang):
    PotraceProcessor.process_file_from_cl(dabenxiang, "yat.png", verbosity=2)
    Image.open("yat.png").show()
