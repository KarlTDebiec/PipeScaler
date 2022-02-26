#!/usr/bin/env python
#   pipescaler/processors/gui/__init__.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""GUI-based Processor stages"""
from __future__ import annotations

from typing import List

from pipescaler.processors.gui.gigapixel_ai_proessor import GigapixelAiProcessor

__all__: List[str] = [
    "GigapixelAiProcessor",
]
