#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image package; contains code specific to image processing.

This module may import from: common, core, pipelines

Package hierarchy (modules may import from any above):
* core / runners / subdivided_image
* pipelines / testing / utilities
* operators
* cli
"""

from __future__ import annotations

from pipescaler.image.subdivided_image import SubdividedImage

__all__ = ["SubdividedImage"]
