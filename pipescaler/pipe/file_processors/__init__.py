#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from pipescaler.pipe.file_processors.pngquant_processor import PngquantProcessor
from pipescaler.pipe.file_processors.texconv_processor import TexconvProcessor

__all__: list[str] = [
    "PngquantProcessor",
    "TexconvProcessor",
]
