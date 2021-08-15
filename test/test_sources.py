#!/usr/bin/env python
#   test_sources.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
####################################### MODULES ########################################
from os import getcwd
from os.path import join

from pipescaler.sources import CitraSource, DirectorySource, DolphinSource, TexmodSource

###################################### VARIABLES #######################################
infiles = {
    f[:-4].upper(): join(getcwd(), "data", "infiles", f)
    for f in ["l.png", "la.png", "rgb.png", "rgba.png"]
}


######################################## TESTS #########################################
def test_directory_source() -> None:
    source = DirectorySource()


def test_citra_source() -> None:
    source = CitraSource()


def test_dolphin_source() -> None:
    source = DolphinSource()


def test_texmod_source() -> None:
    source = TexmodSource()
