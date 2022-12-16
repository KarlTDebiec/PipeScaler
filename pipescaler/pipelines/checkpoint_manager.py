#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Manages checkpoints."""
from logging import info
from os import remove, rmdir
from pathlib import Path
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

        cpt_paths = self.get_cpt_paths(self.directory, images, cpts)
        if all(p.exists() for p in cpt_paths):
            outputs = tuple(
                PipeImage(path=p, parents=i) for i, p in zip(images, cpt_paths)
            )
            info(f"{self}: {images[0].relative_name} checkpoints {cpts} loaded")

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

    def purge_unrecognized_files(self, directory: Optional[Path] = None) -> None:
        """Remove unrecognized files and subdirectories in checkpoint directory."""
        if directory is None:
            directory = self.directory
        for path in directory.iterdir():
            if path.is_dir():
                self.purge_unrecognized_files(path)
            elif path.is_file():
                relative_path = path.relative_to(self.directory)
                checkpoint = (str(relative_path.parent), path.name)
                if checkpoint not in self.observed_checkpoints:
                    remove(path)
                    info(f"{self}: file {relative_path} removed")
            else:
                raise ValueError(f"Unsupported path type: {path}")
        if not any(directory.iterdir()) and directory != self.directory:
            rmdir(directory)
            info(f"{self}: directory {directory.relative_to(self.directory)} removed")

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
        cpt_paths = self.get_cpt_paths(self.directory, images, cpts)
        for i, c, p in zip(images, cpts, cpt_paths):
            if not p.parent.exists():
                p.parent.mkdir(parents=True)
                info(f"{self}: directory {p.parent} created")
            if not p.exists() or overwrite:
                i.save(p)
                info(f"{self}: {i.relative_name} checkpoint {c} saved")
            else:
                i.path = p
            self.observe(i, c)

        return images

    @staticmethod
    def get_cpt_paths(
        root_directory: Path, images: Collection[PipeImage], cpts: Collection[str]
    ) -> list[Path]:
        """Get paths to checkpoints.

        Arguments:
            root_directory: Root directory of checkpoints
            images: Images
            cpts: Names of checkpoints
        Returns:
            Paths to checkpoints
        """
        if len(images) != len(cpts):
            raise ValueError(f"Expected {len(cpts)} inputs but received {len(images)}.")
        cpt_paths = []
        for i, c in zip(images, cpts):
            if i.relative_path:
                cpt_paths.append(root_directory / i.relative_path / i.name / c)
            else:
                cpt_paths.append(root_directory / i.name / c)

        return cpt_paths

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
