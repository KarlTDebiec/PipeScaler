#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler general pipelines package.

This module may import from: common, core

Hierarchy within module:
* checkpoint_manager
* segments / sorters
"""

from __future__ import annotations

from .checkpoint_manager import CheckpointManager

__all__ = [
    "CheckpointManager",
]
