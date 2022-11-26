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

from pipescaler.core.pipelines import CheckpointManagerBase, PostCheckpointedSegment
from pipescaler.core.pipelines.segment import Segment
from pipescaler.core.pipelines.segments.checkpointed.checkpointed_file_processor_segment import (
    CheckpointedFileProcessorSegment,
)
from pipescaler.core.pipelines.segments.checkpointed.post_checkpointed_segment import (
    PreCheckpointedSegment,
)
from pipescaler.core.pipelines.segments.file_processor_segment import (
    FileProcessorSegment,
)


class CheckpointManager(CheckpointManagerBase):
    """Manages checkpoints."""

    def __repr__(self):
        """Representation."""
        return f"{self.__class__.__name__}(directory={self.directory})"

    def post_file_processor(
        self, cpt: str
    ) -> Callable[[Callable[[Path, Path], None]], CheckpointedFileProcessorSegment]:
        def decorator(
            file_processor: Callable[[Path, Path], None]
        ) -> CheckpointedFileProcessorSegment:
            file_processor_segment = FileProcessorSegment(
                file_processor, output_extension=Path(cpt).suffix
            )

            return CheckpointedFileProcessorSegment(file_processor_segment, self, [cpt])

        return decorator

    def post_segment(
        self, *cpts: str, calls: Optional[Collection[Segment]] = None
    ) -> Callable[[Segment], PreCheckpointedSegment]:
        internal_cpts = self.get_internal_cpts(*calls) if calls else []

        def decorator(stage: Segment) -> PreCheckpointedSegment:
            internal_cpts.extend(self.get_internal_cpts(stage))

            return PreCheckpointedSegment(stage, self, cpts, internal_cpts)

        return decorator

    def pre_segment(
        self, *cpts: str, calls: Optional[Collection[Segment]] = None
    ) -> Callable[[Segment], PostCheckpointedSegment]:
        internal_cpts = self.get_internal_cpts(*calls) if calls else []

        def decorator(stage: Segment) -> PostCheckpointedSegment:
            internal_cpts.extend(self.get_internal_cpts(stage))

            return PostCheckpointedSegment(stage, self, cpts, internal_cpts)

        return decorator

    def purge_unrecognized_files(self) -> None:
        """Remove files in output directory that have not been logged as observed."""
        for img in self.directory.iterdir():
            if img.is_dir():
                for cpt in img.iterdir():
                    if cpt.is_dir():
                        rmdir(cpt)
                        info(f"{self}: directory {join(img.name, cpt.name)} removed")
                    elif (img.name, cpt.name) not in self.observed_checkpoints:
                        remove(cpt)
                        info(f"{self}: file {join(img.name, cpt.name)} removed")
                if not any(img.iterdir()):
                    rmdir(img)
                    info(f"{self}: directory {img.name} removed")
            else:
                remove(img)
                info(f"{self}: file {img.name} removed")

    @staticmethod
    def get_internal_cpts(*called_functions: Segment) -> list[str]:
        internal_cpts: list[str] = []
        for function in called_functions:
            if hasattr(function, "cpt"):
                internal_cpts.append(getattr(function, "cpt"))
            if hasattr(function, "cpts"):
                internal_cpts.extend(getattr(function, "cpts"))
            if hasattr(function, "internal_cpts"):
                internal_cpts.extend(getattr(function, "internal_cpts"))
        return internal_cpts
