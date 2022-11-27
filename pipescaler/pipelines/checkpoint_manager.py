#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Manages checkpoints."""
from logging import info
from os import remove, rmdir
from os.path import join
from pathlib import Path
from typing import Callable, Collection, Optional

from pipescaler.core import Runner
from pipescaler.core.pipelines import (
    CheckpointManagerBase,
    PostCheckpointedRunnerSegment,
    PostCheckpointedSegment,
    PreCheckpointedSegment,
    RunnerSegment,
    Segment,
)


class CheckpointManager(CheckpointManagerBase):
    """Manages checkpoints."""

    def __repr__(self):
        """Representation."""
        return f"{self.__class__.__name__}(directory={self.directory})"

    def post_runner(
        self, cpt: str
    ) -> Callable[[Runner], PostCheckpointedRunnerSegment]:
        """Get decorator to wrap Runner to Segment with post-execution checkpoint."""

        def decorator(runner: Runner) -> PostCheckpointedRunnerSegment:
            """Wrap Runner to Segment with post-execution checkpoint."""
            runner_segment = RunnerSegment(runner, output_extension=Path(cpt).suffix)

            return PostCheckpointedRunnerSegment(runner_segment, self, [cpt])

        return decorator

    def post_segment(
        self, *cpts: str, calls: Optional[Collection[Segment]] = None
    ) -> Callable[[Segment], PostCheckpointedSegment]:
        """Get decorator to wrap Segment to Segment with post-execution checkpoint."""
        internal_cpts = self.get_internal_cpts(*calls) if calls else []

        def decorator(stage: Segment) -> PostCheckpointedSegment:
            """Wrap Segment to Segment with post-execution checkpoint."""
            internal_cpts.extend(self.get_internal_cpts(stage))

            return PostCheckpointedSegment(stage, self, cpts, internal_cpts)

        return decorator

    def pre_segment(
        self, *cpts: str, calls: Optional[Collection[Segment]] = None
    ) -> Callable[[Segment], PreCheckpointedSegment]:
        """Get decorator to wrap Segment to Segment with pre-execution checkpoint."""
        internal_cpts = self.get_internal_cpts(*calls) if calls else []

        def decorator(stage: Segment) -> PreCheckpointedSegment:
            """Wrap Segment to Segment with pre-execution checkpoint."""
            internal_cpts.extend(self.get_internal_cpts(stage))

            return PreCheckpointedSegment(stage, self, cpts, internal_cpts)

        return decorator

    def purge_unrecognized_files(self) -> None:
        """Remove files in output directory that have not been logged as observed."""
        for image in self.directory.iterdir():
            if image.is_dir():
                for cpt in image.iterdir():
                    if cpt.is_dir():
                        rmdir(cpt)
                        info(f"{self}: directory {join(image.name, cpt.name)} removed")
                    elif (image.name, cpt.name) not in self.observed_checkpoints:
                        remove(cpt)
                        info(f"{self}: file {join(image.name, cpt.name)} removed")
                if not any(image.iterdir()):
                    rmdir(image)
                    info(f"{self}: directory {image.name} removed")
            else:
                remove(image)
                info(f"{self}: file {image.name} removed")

    @staticmethod
    def get_internal_cpts(*internal_segments: Segment) -> list[str]:
        """Get checkpoints created by Segments contained within another Segment.

        Arguments:
            internal_segments: Internal Segments
        Returns:
            All checkpoints created by internal Segments
        """
        internal_cpts: list[str] = []
        for function in internal_segments:
            if hasattr(function, "cpts"):
                internal_cpts.extend(getattr(function, "cpts"))
            if hasattr(function, "internal_cpts"):
                internal_cpts.extend(getattr(function, "internal_cpts"))
        return internal_cpts
