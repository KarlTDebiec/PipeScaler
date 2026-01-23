#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages checkpoints."""

from __future__ import annotations

from collections.abc import Callable, Collection, Sequence
from itertools import cycle
from logging import info
from os import remove, rmdir
from pathlib import Path

from pipescaler.core.pipelines import CheckpointManagerBase, PipeObject, SegmentLike
from pipescaler.pipelines.segments import (
    PostCheckpointedSegment,
    PreCheckpointedSegment,
)


class CheckpointManager(CheckpointManagerBase):
    """Manages checkpoints."""

    def load(
        self,
        inputs: tuple[PipeObject, ...],
        cpts: Sequence[str],
        *,
        calls: Collection[SegmentLike | str] | None = None,
    ) -> tuple[PipeObject, ...] | None:
        """Load images from checkpoints, if available, otherwise return None.

        If the length of inputs is equal to the length of cpts, inputs and cpts are
        zipped. Otherwise, the first input is used for all cpts.

        Arguments:
            inputs: Input objects
            cpts: Names of checkpoints to load
            calls: Collection of checkpoint names and potentially-checkpointed segments
              used to prepare list of checkpoint names expected to be present whenever
              cpts are present
        Returns:
            Images loaded from checkpoints if available, otherwise None
        """
        cls = inputs[0].__class__

        location_names = list(dict.fromkeys([i.location_name for i in inputs]))
        if len(location_names) not in (1, len(cpts)):
            raise ValueError(
                "Number of input locations must equal either 1 or number of cpts;"
                f"received {len(location_names)} and {len(cpts)}."
            )
        for ln, c in zip(cycle(location_names), cpts):
            self.observe(ln, c)

        cpt_paths = self.get_cpt_paths(self.directory, location_names, cpts)
        if all(p.exists() for p in cpt_paths):
            outputs = tuple(cls(path=p, parents=inputs) for p in cpt_paths)
            location_str = (
                location_names[0] if len(location_names) == 1 else location_names
            )
            cpts_str = cpts[0] if len(cpts) == 1 else cpts
            info(f"{self}: '{location_str}' checkpoints '{cpts_str}' loaded")

            internal_cpts = self.get_cpts_of_segments(*calls) if calls else []
            for ln in location_names:
                for c in internal_cpts:
                    self.observe(ln, c)

            return outputs

        return None

    def post_segment(
        self, *cpts: str, calls: Collection[SegmentLike] | None = None
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

            return PostCheckpointedSegment(
                segment, self, cpts, internal_cpts=internal_cpts
            )

        return decorator

    def pre_segment(
        self, *cpts: str, calls: Collection[SegmentLike] | None = None
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

            return PreCheckpointedSegment(
                segment, self, cpts, internal_cpts=internal_cpts
            )

        return decorator

    def purge_unrecognized_files(self, directory: Path | None = None):
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
                    info(f"{self}: file '{relative_path}' removed")
            else:
                raise ValueError(f"Unsupported path type: {path}")
        if not any(directory.iterdir()) and directory != self.directory:
            rmdir(directory)
            info(f"{self}: directory '{directory.relative_to(self.directory)}' removed")

    def save(
        self,
        inputs: tuple[PipeObject, ...],
        cpts: Collection[str],
        *,
        overwrite: bool = True,
    ) -> tuple[PipeObject, ...]:
        """Save images to checkpoints.

        Arguments:
            inputs: Images
            cpts: Names of checkpoints
            overwrite: Whether to overwrite existing checkpoints
        Returns:
            Images, with paths updated to checkpoints
        """
        if len(inputs) != len(cpts):
            raise ValueError(
                f"Number of cpts ({len(cpts)}) must equal number of images "
                f"({len(inputs)})"
            )
        cpt_paths = self.get_cpt_paths(
            self.directory, [i.location_name for i in inputs], cpts
        )
        for i, c, p in zip(inputs, cpts, cpt_paths):
            if not p.parent.exists():
                p.parent.mkdir(parents=True)
                info(f"{self}: directory '{p.parent}' created")
            if not p.exists() or overwrite:
                i.save(p)
                info(f"{self}: '{i.location_name}' checkpoint '{c}' saved")
            else:
                i.path = p
            self.observe(i.location_name, c)

        return inputs

    @staticmethod
    def get_cpt_paths(
        root_directory: Path, location_names: Collection[str], cpts: Collection[str]
    ) -> list[Path]:
        """Get paths to checkpoints.

        Arguments:
            root_directory: Root directory of checkpoints
            location_names: Locations and names of images
            cpts: Names of checkpoints
        Returns:
            Paths to checkpoints
        """
        cpt_paths = []
        for ln, c in zip(cycle(location_names), cpts):
            cpt_paths.append(root_directory / ln / c)

        return cpt_paths

    @staticmethod
    def get_cpts_of_segments(*cpts_or_segments: SegmentLike | str) -> list[str]:
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
