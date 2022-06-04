#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sorter pipes."""
from abc import ABC

from pipescaler.core.pipe.pipe import Pipe


class SorterPipe(Pipe, ABC):
    pass
