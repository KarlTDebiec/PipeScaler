#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""ESRGAN Models."""
from __future__ import annotations

from pipescaler.models.esrgan.esrgan_1x import Esrgan1x
from pipescaler.models.esrgan.esrgan_4x import Esrgan4x

__all__: list[str] = [
    "Esrgan1x",
    "Esrgan4x",
]
