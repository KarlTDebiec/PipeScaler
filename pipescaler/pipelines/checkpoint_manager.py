#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Manages checkpoints."""
from logging import info
from os import remove, rmdir
from os.path import join
from pathlib import Path
from shutil import rmtree
from typing import Callable, Collection, Optional, Union

from pipescaler.core import RunnerLike
from pipescaler.core.pipelines import CheckpointManagerBase, PipeImage, SegmentLike
from pipescaler.core.pipelines.segments import RunnerSegment
from pipescaler.core.pipelines.segments.checkpointed import (
    PostCheckpointedRunnerSegment,
    PostCheckpointedSegment,
    PreCheckpointedSegment,
)


class CheckpointManager(CheckpointManagerBase):
    """Manages checkpoints."""

    def load(
        self,
        images: tuple[PipeImage, ...],
        cpts: Collection[str],
        *,
        calls: Optional[Collection[Union[SegmentLike, str]]] = None,
    ) -> Optional[tuple[PipeImage, ...]]:
        """Load images from checkpoints, if available, otherwise return None.

        Arguments:
            images: Images
            cpts: Names of checkpoints to load
            calls: Collection of checkpoint names and potentially-checkpointed segments
              used to prepare list of checkpoint names expected to be present whenever
              cpts are present
        Returns:
            Images loaded from checkpoints if available, otherwise None
        """
        for i, c in zip(images, cpts):
            self.observe(i, c)

        cpt_paths = [self.directory / i.name / c for i in images for c in cpts]
        if all(p.exists() for p in cpt_paths):
            outputs = tuple(
                PipeImage(path=p, parents=i) for i, p in zip(images, cpt_paths)
            )
            info(f"{self}: {images[0].name} checkpoints {cpts} loaded")

            internal_cpts = self.get_cpts_of_segments(*calls) if calls else []
            for i in images:
                for c in internal_cpts:
                    self.observe(i, c)

            return outputs

        return None

    def post_runner(
        self, cpt: str
    ) -> Callable[[RunnerLike], PostCheckpointedRunnerSegment]:
        """Get decorator to wrap Runner to Segment with post-execution checkpoint.

        Arguments:
            cpt: Name of checkpoint
        Returns:
            Decorator to wrap Runner to Segment with post-execution checkpoint
        """

        def decorator(runner: RunnerLike) -> PostCheckpointedRunnerSegment:
            """Wrap Runner to Segment with post-execution checkpoint.

            Arguments:
                runner: Runner to wrap
            Returns:
                Segment with post-execution checkpoint
            """
            runner_segment = RunnerSegment(runner, output_extension=Path(cpt).suffix)

            return PostCheckpointedRunnerSegment(runner_segment, self, [cpt])

        return decorator

    def post_segment(
        self, *cpts: str, calls: Optional[Collection[SegmentLike]] = None
    ) -> Callable[[SegmentLike], PostCheckpointedSegment]:
        """Get decorator to wrap Segment to Segment with post-execution checkpoint.

        Arguments:
            cpts: Names of checkpoints
            calls: Segments called within decorated Segment
        Returns:
            Decorator to wrap Segment to Segment with post-execution checkpoint
        """
        internal_cpts = self.get_cpts_of_segments(*calls) if calls else []

        def decorator(segment: SegmentLike) -> PostCheckpointedSegment:
            """Wrap Segment to Segment with post-execution checkpoint.

            Arguments:
                segment: Segment to wrap
            Returns:
                Segment with post-execution checkpoint
            """
            internal_cpts.extend(self.get_cpts_of_segments(segment))

            return PostCheckpointedSegment(segment, self, cpts, internal_cpts)

        return decorator

    def pre_segment(
        self, *cpts: str, calls: Optional[Collection[SegmentLike]] = None
    ) -> Callable[[SegmentLike], PreCheckpointedSegment]:
        """Get decorator to wrap Segment to Segment with pre-execution checkpoint.

        Arguments:
            cpts: Names of checkpoints
            calls: Segments called within decorated Segment
        Returns:
            Decorator to wrap Segment to Segment with pre-execution checkpoint
        """
        internal_cpts = self.get_cpts_of_segments(*calls) if calls else []

        def decorator(segment: SegmentLike) -> PreCheckpointedSegment:
            """Wrap Segment to Segment with pre-execution checkpoint.

            Arguments:
                segment: Segment to wrap
            Returns:
                Segment with pre-execution checkpoint
            """
            internal_cpts.extend(self.get_cpts_of_segments(segment))

            return PreCheckpointedSegment(segment, self, cpts, internal_cpts)

        return decorator

    def purge_unrecognized_files(self) -> None:
        """Remove files in output directory that have not been logged as observed."""
        for image in self.directory.iterdir():
            if image.is_dir():
                for cpt in image.iterdir():
                    if cpt.is_dir():
                        rmtree(cpt)
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

    def save(
        self,
        images: tuple[PipeImage, ...],
        cpts: Collection[str],
        *,
        overwrite: bool = True,
    ) -> tuple[PipeImage, ...]:
        """Save images to checkpoints.

        Arguments:
            images: Images
            cpts: Names of checkpoints
            overwrite: Whether to overwrite existing checkpoints
        Returns:
            Images, with paths updated to checkpoints
        """
        if len(images) != len(cpts):
            raise ValueError(f"Expected {len(cpts)} inputs but received {len(images)}.")
        cpt_paths = [self.directory / i.name / c for i in images for c in cpts]
        for o, c, p in zip(images, cpts, cpt_paths):
            if not p.parent.exists():
                p.parent.mkdir(parents=True)
            if not p.exists() or overwrite:
                o.save(p)
                info(f"{self}: {o.name} checkpoint {c} saved")
            else:
                o.path = p
            self.observe(o, c)

        return images

    @staticmethod
    def get_cpts_of_segments(*cpts_or_segments: Union[SegmentLike, str]) -> list[str]:
        """Get checkpoints created by a collection of Segments.

        Arguments:
            cpts_or_segments: Collection of checkpoint names and
            potentially-checkpointed segments used to prepare list of checkpoint names
        Returns:
            All checkpoint names either provided directly or associated with a provided
            Segment
        """
        cpts: list[str] = []
        for cpt_or_segment in cpts_or_segments:
            if isinstance(cpt_or_segment, str):
                cpts.append(cpt_or_segment)
            else:
                if hasattr(cpt_or_segment, "cpts"):
                    cpts.extend(getattr(cpt_or_segment, "cpts"))
                if hasattr(cpt_or_segment, "internal_cpts"):
                    cpts.extend(getattr(cpt_or_segment, "internal_cpts"))
        return cpts
