#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Type hints for pipelines."""
from __future__ import annotations

from collections.abc import Callable

from pipescaler.core.pipelines.pipe_object import PipeObject
from pipescaler.core.pipelines.segment import Segment

type SegmentLike = Segment | Callable[[PipeObject], tuple[PipeObject, ...]]
"""Type alias for a Segment or callable with the same call signature."""
