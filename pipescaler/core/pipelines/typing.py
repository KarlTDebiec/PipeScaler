#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Type hints for pipelines."""
from __future__ import annotations

from typing import Callable, TypeAlias

from pipescaler.core.pipelines.pipe_object import PipeObject
from pipescaler.core.pipelines.segment import Segment

SegmentLike: TypeAlias = Segment | Callable[[PipeObject], tuple[PipeObject, ...]]
