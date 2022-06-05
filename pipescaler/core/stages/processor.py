#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for processors."""
from __future__ import annotations

from abc import ABC

from pipescaler.core.stage import Stage


class Processor(Stage, ABC):
    """Abstract base class for processors."""

    pass
