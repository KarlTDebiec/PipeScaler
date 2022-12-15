#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment with pre-execution checkpoints."""
from logging import info

from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.segments.checkpointed_segment import CheckpointedSegment


class PreCheckpointedSegment(CheckpointedSegment):
    """Segment with pre-execution checkpoints."""

    def __call__(self, *inputs: PipeImage) -> tuple[PipeImage, ...]:
        """Checkpoint inputs and return outputs of wrapped Segment.

        Input images' paths are set to checkpoint paths before passing on to wrapped
        Segment.

        Arguments:
            inputs: Input images, saved to checkpoints if not already present
        Returns:
            Output images, within a tuple even if only one
        """
        if len(inputs) != len(self.cpts):
            raise ValueError(
                f"Expected {len(self.cpts)} inputs to {self.segment} "
                f"but received {len(inputs)}."
            )

        cpt_paths = [
            self.cp_manager.directory / i.name / c for i in inputs for c in self.cpts
        ]
        for i, c, p in zip(inputs, self.cpts, cpt_paths):
            if p.exists():
                i.path = p
            else:
                i.save(p)
                info(f"{self}: {i.name} checkpoint {p} saved")
            self.cp_manager.observe(i, c)

        return self.segment(*inputs)