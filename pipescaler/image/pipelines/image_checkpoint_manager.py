#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages checkpoints."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pipescaler.core import RunnerLike
from pipescaler.image.core.typing import ImageWriterLike
from pipescaler.pipelines.checkpoint_manager import CheckpointManager

from .segments import (
    CheckpointedImageWriterSegment,
    ImageRunnerSegment,
    PostCheckpointedImageRunnerSegment,
)

__all__ = ["ImageCheckpointManager"]


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

    def post_writer(
        self, cpt: str
    ) -> Callable[[ImageWriterLike], CheckpointedImageWriterSegment]:
        """Wrap an in-process image writer in a resumable checkpoint segment.

        Arguments:
            cpt: checkpoint filename, including the writer's output extension
        Returns:
            decorator accepting a writer of Pillow pixels and an output path
        """

        def decorator(writer: ImageWriterLike) -> CheckpointedImageWriterSegment:
            """Bind a writer to the configured checkpoint.

            Arguments:
                writer: callable accepting Pillow pixels and an output path
            Returns:
                checkpointed image writer segment
            """
            return CheckpointedImageWriterSegment(writer, self, cpt)

        return decorator
