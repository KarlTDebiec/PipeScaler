#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for EsrganSerializer."""
from __future__ import annotations

from pytest import fixture, mark

from pipescaler.common import temporary_filename
from pipescaler.testing import get_model_infile, skip_if_ci
from pipescaler.utilities.esrgan_serializer import EsrganSerializer


@fixture
def utility(request) -> EsrganSerializer:
    return EsrganSerializer()


@mark.parametrize(
    ("infile"),
    [
        skip_if_ci()("ESRGAN/1x_BC1-smooth2"),
        skip_if_ci()("ESRGAN/RRDB_ESRGAN_x4"),
        skip_if_ci()("ESRGAN/RRDB_ESRGAN_x4_old_arch"),
    ],
)
def test(infile: str, utility: EsrganSerializer) -> None:
    infile = get_model_infile(infile)
    with temporary_filename(".pth") as outfile:
        utility(infile, outfile)
