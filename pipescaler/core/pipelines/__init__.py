#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes for and functions related to pipelines."""
from __future__ import annotations

from pipescaler.core.pipelines.functions import (
    wrap_merger,
    wrap_processor,
    wrap_splitter,
)
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.source import Source
from pipescaler.core.pipelines.terminus import Terminus

__all__: list[str] = [
    "PipeImage",
    "Source",
    "Terminus",
    "wrap_merger",
    "wrap_processor",
    "wrap_splitter",
]
