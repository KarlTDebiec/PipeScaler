#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment with pre-execution checkpoint(s)."""
from logging import info
from typing import Sequence, Union

from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.segments.checkpointed_segment import CheckpointedSegment


class PreCheckpointedSegment(CheckpointedSegment):
    """Segment with pre-execution checkpoint(s)."""

    def __call__(self, *inputs: PipeImage) -> Union[PipeImage, Sequence[PipeImage]]:
        """Receives input images and returns output images.

        Arguments:
            inputs: Input image(s), saved to checkpoint(s) if not already present
        Returns:
            Output image(s)
        """
        if len(inputs) != len(self.cpts):
            raise ValueError(
                f"Expected {len(self.cpts)} inputs but received {len(inputs)}."
            )

        cpt_paths = [
            self.cp_manager.directory / i.name / cpt
            for i in inputs
            for cpt in self.cpts
        ]
        if not all(cpt_path.exists() for cpt_path in cpt_paths):
            for i, cpt, cpt_path in zip(inputs, self.cpts, cpt_paths):
                i.save(cpt_path)
                info(f"{self}: {i.name} checkpoint {cpt} saved")
        for i in inputs:
            for c in self.cpts:
                self.cp_manager.observe(i, c)

        return self.segment(*inputs)
