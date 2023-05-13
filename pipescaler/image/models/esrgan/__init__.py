#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image ESRGAN models package."""
from __future__ import annotations

from pipescaler.image.models.esrgan.esrgan import Esrgan
from pipescaler.image.models.esrgan.esrgan_1x import Esrgan1x
from pipescaler.image.models.esrgan.esrgan_4x import Esrgan4x

__all__ = [
    "Esrgan",
    "Esrgan1x",
    "Esrgan4x",
]
