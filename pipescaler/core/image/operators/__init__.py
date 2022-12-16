#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image operator abstract base classes."""
from __future__ import annotations

from pipescaler.core.image.operators.merger import Merger
from pipescaler.core.image.operators.processor import Processor
from pipescaler.core.image.operators.pytorch_processor import PyTorchProcessor
from pipescaler.core.image.operators.splitter import Splitter

__all__ = [
    "Merger",
    "Processor",
    "PyTorchProcessor",
    "Splitter",
]
