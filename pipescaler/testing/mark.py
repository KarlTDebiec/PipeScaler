#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Marks for testing."""
from functools import partial
from os import getenv
from platform import system
from typing import Type

from pytest import mark, param

from pipescaler.common import UnsupportedPlatformError
from pipescaler.core.exceptions import UnsupportedImageModeError


def skip_if_ci(inner: partial = None) -> partial:
    """Mark test to skip if running within continuous integration pipeline.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [
        mark.skipif(
            getenv("CI") is not None,
            reason="Skip when running in CI",
        )
    ]
    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)


def xfail_file_not_found(inner: partial = None) -> partial:
    """Mark test to be expected to fail due to a file that cannot be found.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = mark.xfail(raises=FileNotFoundError)
    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)


def xfail_if_platform(
    unsupported_platforms: set[str] = None,
    raises: Type[Exception] = UnsupportedPlatformError,
    inner: partial = None,
) -> partial:
    """Mark test to be expected to fail on selected platforms.

    Arguments:
        unsupported_platforms: Platforms on which test should be expected to fail
        raises: Error test should be expected to raise
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = mark.xfail(
        system() in unsupported_platforms,
        raises=raises,
        reason=f"Not supported on {system()}",
    )

    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)


def xfail_unsupported_image_mode(inner: partial = None) -> partial:
    """Mark test to be expected to fail due to an unsupported image mode.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = mark.xfail(raises=UnsupportedImageModeError)
    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)


def xfail_value(inner: partial = None) -> partial:
    """Mark test to be expected to fail due to a value error.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = mark.xfail(raises=ValueError)
    if inner is not None:
        marks.append(inner.keywords["marks"].mark)
    return partial(param, marks=marks)
