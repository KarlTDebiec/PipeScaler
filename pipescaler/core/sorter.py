#!/usr/bin/env python
#   pipescaler/sorters/sorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import ABC

from pipescaler.core.stage import Stage


####################################### CLASSES ########################################
class Sorter(Stage, ABC):
    pass
