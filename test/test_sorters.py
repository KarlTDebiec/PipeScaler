#!/usr/bin/env python
#   test_sorters.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
####################################### MODULES ########################################
from os import getcwd
from os.path import join

from pipescaler.sorters import (
    AlphaSorter,
    GrayscaleSorter,
    ListSorter,
    ModeSorter,
    RegexSorter,
    SizeSorter,
    SolidColorSorter,
)

###################################### VARIABLES #######################################


infiles = {
    f[:-4].upper(): join(getcwd(), "data", "infiles", f)
    for f in ["l.png", "la.png", "rgb.png", "rgba.png"]
}


######################################## TESTS #########################################
def test_alpha_sorter() -> None:
    sorter = AlphaSorter()


def test_grayscale_sorter() -> None:
    sorter = GrayscaleSorter()


def test_list_sorter() -> None:
    sorter = ListSorter()


def test_mode_sorter() -> None:
    sorter = ModeSorter()


def test_regex_sorter() -> None:
    sorter = RegexSorter()


def test_size_sorter() -> None:
    sorter = SizeSorter()


def test_solid_color_sorter() -> None:
    sorter = SolidColorSorter()
