#!/usr/bin/env python3
#   test.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################

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
def cltool(request):
    return request.param


#################################### TESTS ####################################
def test_construct_argparser(cltool):
    cltool.construct_argparser()
