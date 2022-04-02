#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for WaifuSerializer."""
from __future__ import annotations

from pytest import fixture, mark

from pipescaler.common import temporary_filename
from pipescaler.testing import get_model_infile, skip_if_ci
from pipescaler.utilities import WaifuSerializer


@fixture
def utility(request) -> WaifuSerializer:
    return WaifuSerializer()


@mark.parametrize(
    ("architecture", "infile"),
    [
        skip_if_ci()("upconv7", "WaifuUpConv7/a-2-1.json"),
        skip_if_ci()("vgg7", "WaifuVgg7/a-2-1.json"),
    ],
)
def test(architecture: str, infile: str, utility: WaifuSerializer) -> None:
    infile = get_model_infile(infile)
    with temporary_filename(".png") as outfile:
        utility(architecture, infile, outfile)
