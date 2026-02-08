#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image pipeline termini package.

This module may import from: common, core.pipelines, image.core.pipelines

Hierarchy within module:
* image_directory_terminus
"""

from __future__ import annotations

from .image_directory_terminus import (
    ImageDirectoryTerminus,
)

__all__ = [
    "ImageDirectoryTerminus",
]
