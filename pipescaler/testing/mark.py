#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Marks for testing."""
from __future__ import annotations

from functools import partial
from os import getenv
from platform import system
from typing import Any, Type

from pytest import mark, param

from pipescaler.common import UnsupportedPlatformError


def parametrize_with_readable_ids(*args, **kwargs) -> partial:
    """Parametrize test with readable IDs.

    Arguments:
        *args: Additional arguments
        **kwargs: Additional keyword arguments
    Returns:
        mark.parametrize, with readable IDs
    """

    def get_names(arguments: Any) -> str:
        """Get readable names for arguments.

        Arguments:
            arguments: arguments
        Returns:
            str: Readable names
        """

        def get_name(argument: Any) -> str:
            """Get readable name for an argument.

            Arguments:
                argument: argument
            Returns:
                str: Readable name
            """
            return argument.__name__

        if isinstance(arguments, tuple):
            return f"{'-'.join(map(get_name, arguments))}"
        return get_name(arguments)

    return partial(mark.parametrize(ids=get_names, *args, **kwargs))


def skip_if_ci(inner: partial | None = None) -> partial:
    """Mark test to skip if running within continuous integration pipeline.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [mark.skipif(getenv("CI") is not None, reason="Skip when running in CI")]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)


def xfail_file_not_found(inner: partial | None = None) -> partial:
    """Mark test to be expected to fail due to a file that cannot be found.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [mark.xfail(raises=FileNotFoundError)]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)


def xfail_if_platform(
    unsupported_platforms: set[str] | None = None,
    raises: Type[Exception] = UnsupportedPlatformError,
    inner: partial | None = None,
) -> partial:
    """Mark test to be expected to fail on selected platforms.

    Arguments:
        unsupported_platforms: Platforms on which test should be expected to fail
        raises: Error test should be expected to raise
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    if not unsupported_platforms:
        unsupported_platforms = set()
    marks = [
        mark.xfail(
            system() in unsupported_platforms,
            raises=raises,
            reason=f"Not supported on {system()}",
        )
    ]

    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)


def xfail_system_exit(inner: partial | None = None) -> partial:
    """Mark test to be expected to fail due to a system exit.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [mark.xfail(raises=SystemExit)]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)


def xfail_value(inner: partial | None = None) -> partial:
    """Mark test to be expected to fail due to a value error.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [mark.xfail(raises=ValueError)]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)
