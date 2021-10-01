#!/usr/bin/env python
#   test_sorters.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
from typing import Dict, List

import pytest

from pipescaler.sorters import (
    AlphaSorter,
    GrayscaleSorter,
    ListSorter,
    ModeSorter,
    RegexSorter,
    SizeSorter,
    SolidColorSorter,
)
from shared import infile_subfolders, infiles


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        (infiles["L"], "no_alpha"),
        (infiles["L_LA"], "drop_alpha"),
        (infiles["LA"], "keep_alpha"),
        (infiles["RGB"], "no_alpha"),
        (infiles["RGB_RGBA"], "drop_alpha"),
        (infiles["RGBA"], "keep_alpha"),
        (infiles["PL"], "no_alpha"),
        (infiles["PLA"], "keep_alpha"),
        (infiles["PRGB"], "no_alpha"),
        (infiles["PRGBA"], "keep_alpha"),
    ],
)
def test_alpha_sorter(infile: str, outlet: str) -> None:
    sorter = AlphaSorter()
    assert sorter(infile) == outlet


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        (infiles["L"], "no_rgb"),
        (infiles["LA"], "no_rgb"),
        (infiles["RGB"], "keep_rgb"),
        (infiles["RGBA"], "keep_rgb"),
        (infiles["PL"], "no_rgb"),
        (infiles["PLA"], "no_rgb"),
        (infiles["PRGB"], "keep_rgb"),
        (infiles["PRGBA"], "keep_rgb"),
    ],
)
def test_grayscale_sorter(infile: str, outlet: str) -> None:
    sorter = GrayscaleSorter()
    assert sorter(infile) == outlet


@pytest.mark.parametrize("outlets", [infile_subfolders])
def test_list_sorter(outlets: Dict[str, List[str]]) -> None:
    sorter = ListSorter(outlets)


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        (infiles["L"], "l"),
        (infiles["LA"], "la"),
        (infiles["RGB"], "rgb"),
        (infiles["RGBA"], "rgba"),
        (infiles["PL"], "l"),
        (infiles["PLA"], "la"),
        (infiles["PRGB"], "rgb"),
        (infiles["PRGBA"], "rgba"),
    ],
)
def test_mode_sorter(infile: str, outlet: str) -> None:
    sorter = ModeSorter()
    assert sorter(infile) == outlet


@pytest.mark.parametrize(
    ("regex", "infile", "outlet"),
    [
        ("basic", infiles["L"], "matched"),
        ("extra", infiles["L"], "unmatched"),
        ("extra", infiles["L_LA"], "matched"),
    ],
)
def test_regex_sorter(regex: str, infile: str, outlet: str) -> None:
    sorter = RegexSorter(regex)
    assert sorter(infile) == outlet


@pytest.mark.parametrize(
    ("cutoff", "infile", "outlet"),
    [
        (64, infiles["L"], "greater_than_or_equal_to"),
        (128, infiles["L"], "greater_than_or_equal_to"),
        (256, infiles["L"], "less_than"),
    ],
)
def test_size_sorter(cutoff: int, infile: str, outlet: str) -> None:
    sorter = SizeSorter(cutoff)
    assert sorter(infile) == outlet


@pytest.mark.parametrize(
    ("infile", "outlet"),
    [
        (infiles["L"], "not_solid"),
        (infiles["L_solid"], "solid"),
        (infiles["LA"], "not_solid"),
        (infiles["LA_solid"], "solid"),
        (infiles["RGB"], "not_solid"),
        (infiles["RGB_solid"], "solid"),
        (infiles["RGBA"], "not_solid"),
        (infiles["RGBA_solid"], "solid"),
        (infiles["PL"], "not_solid"),
        (infiles["PL_solid"], "solid"),
        (infiles["PLA"], "not_solid"),
        (infiles["PLA_solid"], "solid"),
        (infiles["PRGB"], "not_solid"),
        (infiles["PRGB_solid"], "solid"),
        (infiles["PRGBA"], "not_solid"),
        (infiles["PRGBA_solid"], "solid"),
    ],
)
def test_solid_color_sorter(infile: str, outlet: str) -> None:
    sorter = SolidColorSorter()
    assert sorter(infile) == outlet
