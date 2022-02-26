#!/usr/bin/env python
#   pipescaler/testing/fixture.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Fixtures for testing"""
from functools import partial
from typing import Any, Dict, List, Type

from pytest import fixture

from pipescaler.core import Stage


def stage_fixture(cls: Type[Stage], params: List[Dict[str, Any]]):
    """
    Decorator for Pipescaler Stage test fixtures, which provides clearer ids that make
    test output easier to read

    Args:
        cls: Stage test fixture class
        params: Fixture parameters

    Returns:
        Fixture with provided params and clear ids
    """

    def get_name(args):
        return f"{cls.__name__}({','.join(map(str, args.values()))})"

    return partial(fixture(params=params, ids=get_name))
