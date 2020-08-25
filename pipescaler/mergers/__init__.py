#!/usr/bin/env python
#   pipescaler/mergers/__init__.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import List

from pipescaler.mergers.alpha_merger import AlphaMerger

####################################### CLASSES ########################################
__all__: List[str] = ["AlphaMerger"]
