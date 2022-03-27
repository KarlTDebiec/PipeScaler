#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Splitter stages"""
from __future__ import annotations

from typing import List

from pipescaler.splitters.alpha_splitter import AlphaSplitter
from pipescaler.splitters.normal_splitter import NormalSplitter
from pipescaler.splitters.repeat_splitter import RepeatSplitter

__all__: List[str] = ["AlphaSplitter", "NormalSplitter", "RepeatSplitter"]
