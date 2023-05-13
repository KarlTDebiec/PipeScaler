#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages checkpoints."""
from pathlib import Path
from typing import Callable

from pipescaler.core import RunnerLike
from pipescaler.image.pipelines.segments import (
    ImageRunnerSegment,
    PostCheckpointedImageRunnerSegment,
)
from pipescaler.pipelines.checkpoint_manager import CheckpointManager


class ImageCheckpointManager(CheckpointManager):
    """Manages checkpoints."""

    def post_runner(
        self, cpt: str
    ) -> Callable[[RunnerLike], PostCheckpointedImageRunnerSegment]:
        """Get decorator to wrap Runner to Segment with post-execution checkpoint.

        Arguments:
            cpt: Name of checkpoint
        Returns:
            Decorator to wrap Runner to Segment with post-execution checkpoint
        """

        def decorator(runner: RunnerLike) -> PostCheckpointedImageRunnerSegment:
            """Wrap Runner to Segment with post-execution checkpoint.

            Arguments:
                runner: Runner to wrap
            Returns:
                Segment with post-execution checkpoint
            """
            runner_segment = ImageRunnerSegment(
                runner, output_extension=Path(cpt).suffix
            )

            return PostCheckpointedImageRunnerSegment(runner_segment, self, [cpt])

        return decorator
