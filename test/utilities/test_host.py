#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for Host."""
from __future__ import annotations

from pipescaler.image.processors import XbrzProcessor
from pipescaler.testing import parametrized_fixture
from pipescaler.utilities import Host


@parametrized_fixture(
    cls=XbrzProcessor,
    params=[
        {"scale": 2},
    ],
)
def xbrz_processor(request) -> XbrzProcessor:
    return XbrzProcessor(**request.param)


def test(xbrz_processor: XbrzProcessor) -> None:
    Host(processors={"xbrz-2": xbrz_processor})
