#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from abc import ABC
from typing import Optional, Sequence

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.segment import Segment


class CheckpointedSegment(Segment, ABC):
    segment: Segment
    cp_manager: CheckpointManagerBase
    cpts: Sequence[str]
    internal_cpts: Sequence[str]

    def __init__(
        self,
        segment: Segment,
        cp_manager: CheckpointManagerBase,
        cpts: Sequence[str],
        internal_cpts: Optional[Sequence[str]] = None,
    ) -> None:
        self.segment = segment
        self.cp_manager = cp_manager
        self.cpts = cpts
        self.internal_cpts = internal_cpts or []
