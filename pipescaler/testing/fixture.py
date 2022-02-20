#!/usr/bin/env python
#   pipescaler/testing/fixture.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Pipescaler testing fixtures"""
from functools import partial
from typing import Any, Dict, List

from pytest import fixture


def stage_fixture(cls: object, params: List[Dict[str, Any]]):
    def get_name(args):
        return f"{cls.__name__}({','.join(map(str, args.values()))})"

    return partial(fixture(params=params, ids=get_name))
