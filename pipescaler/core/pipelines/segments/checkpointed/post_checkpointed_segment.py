#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment with post-execution checkpoint(s)."""
from logging import info
from typing import Collection, Union

from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.segments.checkpointed_segment import CheckpointedSegment


class PostCheckpointedSegment(CheckpointedSegment):
    """Segment with post-execution checkpoint(s)."""

    def __call__(self, *inputs: PipeImage) -> Union[PipeImage, Collection[PipeImage]]:
        """Receives input images and returns output images.

        Arguments:
            inputs: Input image(s)
        Returns:
            Output image(s), loaded from checkpoint if available
        """
        [self.cp_manager.observe(i, c) for i in inputs for c in self.cpts]

        cpt_paths = [
            self.cp_manager.directory / i.name / cpt
            for i in inputs
            for cpt in self.cpts
        ]
        if all(cpt_cath.exists() for cpt_cath in cpt_paths):
            outputs = tuple(PipeImage(path=c, parents=inputs) for c in cpt_paths)
            info(f"{self}: {inputs[0].name} checkpoints {self.cpts} loaded")
        else:
            outputs = self.segment(*inputs)
            if isinstance(outputs, PipeImage):
                if len(self.cpts) != 1:
                    raise ValueError(
                        f"Expected {len(self.cpts)} outputs but received 1."
                    )
                if not cpt_paths[0].parent.exists():
                    cpt_paths[0].parent.mkdir(parents=True)
                outputs.save(cpt_paths[0])
                info(f"{self}: {outputs.name} checkpoint {self.cpts[0]} saved")
            else:
                if len(outputs) != len(self.cpts):
                    raise ValueError(
                        f"Expected {len(self.cpts)} outputs but received {len(outputs)}."
                    )
                if not cpt_paths[0].parent.exists():
                    cpt_paths[0].parent.mkdir(parents=True)
                for output_pimg, cpt_path in zip(outputs, cpt_paths):
                    output_pimg.save(cpt_path)
                    info(f"{self}: {output_pimg.name} checkpoint {cpt_path} saved")

        return outputs
