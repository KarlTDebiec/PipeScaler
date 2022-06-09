#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Definitions for type hinting."""
from typing import Callable, Union

from core.pipe_image import PipeImage

PipeFunction = Union[
    Callable[[PipeImage], PipeImage],
    Callable[[PipeImage], tuple[PipeImage, ...]],
]
