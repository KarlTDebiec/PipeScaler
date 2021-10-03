#!/usr/bin/env python
#   pipescaler/splitters/__init__.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from typing import List

from pipescaler.splitters.alpha_splitter import AlphaSplitter
from pipescaler.splitters.normal_splitter import NormalSplitter

__all__: List[str] = ["AlphaSplitter", "NormalSplitter"]
