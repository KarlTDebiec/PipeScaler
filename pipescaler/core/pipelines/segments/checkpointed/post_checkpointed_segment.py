#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment with post-execution checkpoints."""
from logging import info

from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.segments.checkpointed_segment import CheckpointedSegment


class PostCheckpointedSegment(CheckpointedSegment):
    """Segment with post-execution checkpoints."""

    def __call__(self, *inputs: PipeImage) -> tuple[PipeImage, ...]:
        """Return outputs of wrapped Segment, loaded from checkpoints if available.

        Arguments:
            inputs: Input images
        Returns:
            Output images, loaded from checkpoint if available, within a tuple even if
            only one
        """
        cpt_paths = [
            self.cp_manager.directory / i.name / c for i in inputs for c in self.cpts
        ]
        if all(p.exists() for p in cpt_paths):
            outputs = tuple(PipeImage(path=p, parents=inputs) for p in cpt_paths)
            info(f"{self}: {inputs[0].name} checkpoints {self.cpts} loaded")
            for i in inputs:
                for c in self.internal_cpts:
                    self.cp_manager.observe(i, c)
        else:
            outputs = self.segment(*inputs)
            if len(outputs) != len(self.cpts):
                raise ValueError(
                    f"Expected {len(self.cpts)} outputs from {self.segment} "
                    f"but received {len(outputs)}."
                )
            if not cpt_paths[0].parent.exists():
                cpt_paths[0].parent.mkdir(parents=True)
            for o, p in zip(outputs, cpt_paths):
                o.save(p)
                info(f"{self}: {o.name} checkpoint {p} saved")
        for i in inputs:
            for c in self.cpts:
                self.cp_manager.observe(i, c)

        return outputs