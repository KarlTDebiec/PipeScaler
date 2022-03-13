#!/usr/bin/env python
#   test/splitters/test_repeat_splitter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Tests for RepeatSplitter"""
import numpy as np
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.splitters import RepeatSplitter
from pipescaler.testing import get_infile, stage_fixture


@stage_fixture(cls=RepeatSplitter, params=[{}])
def splitter(request) -> RepeatSplitter:
    return RepeatSplitter(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        ("1"),
        ("L"),
        ("LA"),
        ("RGB"),
        ("RGBA"),
    ],
)
def test(infile: str, splitter: RepeatSplitter) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as one_outfile:
        with temporary_filename(".png") as two_outfile:
            input_image = Image.open(infile)

            splitter(infile, one=one_outfile, two=two_outfile)

            with Image.open(one_outfile) as one_image:
                with Image.open(two_outfile) as two_image:
                    # noinspection PyTypeChecker
                    assert np.all(np.array(one_image) == np.array(input_image))
                    # noinspection PyTypeChecker
                    assert np.all(np.array(two_image) == np.array(input_image))
