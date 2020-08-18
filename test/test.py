#!/usr/bin/env python3
#   test.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from pipescaler.processors import (ESRGANProcessor, Pixelmator2xProcessor,
                                   PotraceProcessor, ThresholdProcessor,
                                   WaifuPixelmator2xTransparentProcessor,
                                   WaifuProcessor)


#################################### TESTS ####################################
def test_test():
    ESRGANProcessor.construct_argparser()
    Pixelmator2xProcessor.construct_argparser()
    PotraceProcessor.construct_argparser()
    ThresholdProcessor.construct_argparser()
    WaifuPixelmator2xTransparentProcessor.construct_argparser()
    WaifuProcessor.construct_argparser()
