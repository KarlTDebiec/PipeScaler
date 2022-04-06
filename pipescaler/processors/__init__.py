#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Processor stages."""
from __future__ import annotations

from pipescaler.processors.side_channel_processor import SideChannelProcessor
from pipescaler.processors.web_processor import WebProcessor

__all__: list[str] = [
    "SideChannelProcessor",
    "WebProcessor",
]
