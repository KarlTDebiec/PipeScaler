#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""In-process image file writers.

This module may import from: common

Package hierarchy (modules may import from any above):
* dds_writer
"""

from __future__ import annotations

from .dds_writer import DdsWriter

__all__ = ["DdsWriter"]
