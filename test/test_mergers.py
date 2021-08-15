#!/usr/bin/env python
#   test_merges.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
####################################### MODULES ########################################
from os import getcwd
from os.path import join

from pipescaler.mergers import AlphaMerger, ColorToAlphaMerger, NormalMerger

###################################### VARIABLES #######################################
infiles = {
    f[:-4].upper(): join(getcwd(), "data", "infiles", f)
    for f in ["l.png", "la.png", "rgb.png", "rgba.png"]
}


######################################## TESTS #########################################
def test_alpha_merger() -> None:
    merger = AlphaMerger()


def test_color_to_alpha_merger() -> None:
    merger = ColorToAlphaMerger()


def test_normal_merger() -> None:
    merger = NormalMerger()
