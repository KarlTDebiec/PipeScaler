#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info
from typing import Callable

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.pipe_image import PipeImage


class PipeProcessorWithPostCheckpoint:
    """Wraps a PipeProcessor to add checkpointing."""

    cpt: str
    internal_cpts: list[str]

    def __init__(
        self,
        processor: Callable[[PipeImage], PipeImage],
        cp_manager: CheckpointManagerBase,
        cpt: str,
        internal_cpts: list[str],
    ) -> None:
        self.processor = processor
        self.cp_manager = cp_manager
        self.cpt = cpt
        self.internal_cpts = internal_cpts

    def __call__(self, input_pimg: PipeImage) -> PipeImage:
        self.cp_manager.observe(input_pimg, self.cpt)
        for internal_cpt in self.internal_cpts:
            self.cp_manager.observe(input_pimg, internal_cpt)

        cpt_path = self.cp_manager.directory / input_pimg.name / self.cpt
        if cpt_path.exists():
            output_pimg = PipeImage(path=cpt_path, parents=input_pimg)
            info(f"{self}: {output_pimg.name} checkpoint {self.cpt} loaded")
        else:
            output_pimg = self.processor(input_pimg)
            if not cpt_path.parent.exists():
                cpt_path.parent.mkdir(parents=True)
            output_pimg.save(cpt_path)
            info(f"{self}: {output_pimg.name} checkpoint {self.cpt} saved")

        return output_pimg
