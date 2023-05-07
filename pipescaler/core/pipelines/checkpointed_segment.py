#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Segments with checkpoints."""
from __future__ import annotations

from abc import ABC
from typing import Sequence

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.segment import Segment
from pipescaler.core.pipelines.typing import SegmentLike


class CheckpointedSegment(Segment, ABC):
    """Abstract base class for Segments with checkpoints."""

    segment: SegmentLike

    def __init__(
        self,
        segment: SegmentLike,
        cp_manager: CheckpointManagerBase,
        cpts: Sequence[str],
        *,
        internal_cpts: Sequence[str] | None = None,
    ) -> None:
        """Initialize.

        Arguments:
            segment: Segment to apply
            cp_manager: Checkpoint manager
            cpts: Checkpoints to save
            internal_cpts: Names of additional checkpoints saved by Segments within
              this Segment
        """
        if len(cpts) == 0:
            raise ValueError(
                f"{self.__class__.__name__} requires at least one checkpoint."
            )
        if not hasattr(segment, "__call__"):
            raise ValueError(
                f"{self.__class__.__name__} requires a callable Segment; "
                f"{self.segment.__class__.__name__} is not callable."
            )

        self.segment = segment
        """Segment to apply"""
        self.cp_manager = cp_manager
        """Checkpoint manager"""
        self.cpts = cpts
        """Names of checkpoints to save"""
        self.internal_cpts = internal_cpts or []
        """Names of additional checkpoints saved by Segments within this Segment"""

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"segment={self.segment!r}, "
            f"cp_manager={self.cp_manager!r}, "
            f"cpts={self.cpts!r}, "
            f"internal_cpts={self.internal_cpts!r})"
        )
