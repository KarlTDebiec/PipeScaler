#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for Host."""
from __future__ import annotations

import yaml
from pytest import fixture

from pipescaler.utilities import Host


@fixture()
def conf():
    return """
stages:
    xbrz-2:
        XbrzProcessor:
            scale: 2
"""


def test(conf: str) -> None:
    Host(**yaml.load(conf, Loader=yaml.SafeLoader))
