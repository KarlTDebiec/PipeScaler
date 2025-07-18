#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies a Runner with a post-execution checkpoint."""

from __future__ import annotations

from collections.abc import Sequence
from logging import info

from pipescaler.common.file import get_temp_file_path
from pipescaler.core.pipelines import CheckpointedSegment, CheckpointManagerBase
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.segments.image_runner_segment import ImageRunnerSegment


class PostCheckpointedImageRunnerSegment(CheckpointedSegment):
    """Segment that applies a Runner with a post-execution checkpoint."""

    segment: ImageRunnerSegment

    def __init__(
        self,
        segment: ImageRunnerSegment,
        cp_manager: CheckpointManagerBase,
        cpts: Sequence[str],
        internal_cpts: Sequence[str] | None = None,
    ) -> None:
        """Initialize.

        Arguments:
            segment: Segment to apply
            cp_manager: Checkpoint manager
            cpts: Checkpoints to save
            internal_cpts: Checkpoints to save internally
        """
        if len(cpts) != 1:
            raise ValueError(
                f"{self} requires exactly one checkpoint but received {len(cpts)}."
            )
        internal_cpts = internal_cpts or []
        if len(internal_cpts) != 0:
            raise ValueError(
                f"{self} does not support internal checkpoints but received "
                f"{len(internal_cpts)}."
            )
        super().__init__(segment, cp_manager, cpts, internal_cpts=internal_cpts)

    def __call__(self, *input_objs: PipeImage) -> tuple[PipeImage, ...]:
        """Return outputs of wrapped Segment, loaded from checkpoints if available.

        Arguments:
            input_objs: Input images
        Returns:
            Output images, loaded from checkpoint if available, within a tuple for
            consistency with other Segments
        """
        cpt_path = (
            self.cp_manager.directory / input_objs[0].location_name / self.cpts[0]
        )
        if cpt_path.exists():
            output = PipeImage(path=cpt_path, parents=input_objs)
            info(
                f"{self}: '{input_objs[0].location_name}' checkpoints "
                f"'{self.cpts}' loaded"
            )
        else:
            if not cpt_path.parent.exists():
                cpt_path.parent.mkdir(parents=True)
            if input_objs[0].path is None:
                with get_temp_file_path(self.segment.input_extension) as input_path:
                    input_objs[0].image.save(input_path)
                    self.segment.runner(input_path, cpt_path)
            else:
                self.segment.runner(input_objs[0].path, cpt_path)
            output = PipeImage(path=cpt_path, parents=input_objs[0])
            info(f"{self}: '{output.location_name}' checkpoint '{self.cpts[0]}' saved")
        self.cp_manager.observe(input_objs[0].location_name, self.cpts[0])

        return (output,)
