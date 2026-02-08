#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler general pipeline segments package.

This module may import from: common, core.pipelines

Hierarchy within module:
* pre_checkpointed_segment / post_checkpointed_segment
"""

from __future__ import annotations

from .post_checkpointed_segment import (
    PostCheckpointedSegment,
)
from .pre_checkpointed_segment import (
    PreCheckpointedSegment,
)

__all__ = [
    "PostCheckpointedSegment",
    "PreCheckpointedSegment",
]
