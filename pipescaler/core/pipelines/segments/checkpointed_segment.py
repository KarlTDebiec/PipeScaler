#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment with checkpoints."""
from abc import ABC
from typing import Optional, Sequence

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.segment import Segment


class CheckpointedSegment(Segment, ABC):
    """Segment with checkpoints."""

    segment: Segment

    def __init__(
        self,
        segment: Segment,
        cp_manager: CheckpointManagerBase,
        cpts: Sequence[str],
        internal_cpts: Optional[Sequence[str]] = None,
    ) -> None:
        """Initializes.

        Arguments:
            segment: Segment to apply
            cp_manager: Checkpoint manager
            cpts: Checkpoints to save
            internal_cpts: Checkpoints to save internally
        """
        self.segment = segment
        """Segment through which to run images"""
        self.cp_manager = cp_manager
        """Checkpoint manager"""
        self.cpts = cpts
        """Names of checkpoints to save"""
        self.internal_cpts = internal_cpts or []
        """Names of additional checkpoints saved by segments within this segment"""
