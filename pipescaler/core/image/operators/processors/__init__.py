#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes for image processors."""
from __future__ import annotations

from pipescaler.core.image.operators.processors.pytorch_processor import (
    PyTorchProcessor,
)

__all__: list[str] = [
    "PyTorchProcessor",
]
