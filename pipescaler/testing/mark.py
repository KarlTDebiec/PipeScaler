#!/usr/bin/env python
#   pipescaler/testing/mark.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Marks for testing"""
from functools import partial
from os import getenv
from platform import system
from typing import Set, Type

from pytest import mark, param

from pipescaler.common import UnsupportedPlatformError
from pipescaler.core import UnsupportedImageModeError


def skip_if_ci(inner=None):
    marks = [
        mark.skipif(
            getenv("CI") is not None,
            reason="Skip when running in CI",
        )
    ]
    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)


def xfail_file_not_found(inner=None):
    marks = mark.xfail(raises=FileNotFoundError)
    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)


def xfail_if_platform(
    unsupported_platforms: Set[str] = None,
    raises: Type[Exception] = UnsupportedPlatformError,
    inner=None,
):
    marks = mark.xfail(
        system() in unsupported_platforms,
        raises=raises,
        reason=f"Not supported on {system()}",
    )

    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)


def xfail_unsupported_image_mode(inner=None):
    marks = mark.xfail(raises=UnsupportedImageModeError)
    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)


def xfail_value(inner=None):
    marks = mark.xfail(raises=ValueError)
    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)
