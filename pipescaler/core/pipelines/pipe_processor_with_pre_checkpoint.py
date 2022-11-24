#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info
from typing import Callable, Collection, Union

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.pipe_image import PipeImage


class PipeProcessorWithPreCheckpoint:
    """Wraps a PipeProcessor to add checkpointing."""

    cpt: str
    internal_cpts: list[str]

    def __init__(
        self,
        operator: Union[
            Callable[[PipeImage], PipeImage],
            Callable[[PipeImage], Collection[PipeImage]],
        ],
        cp_manager: CheckpointManagerBase,
        cpt: str,
        internal_cpts: list[str],
    ) -> None:
        self.processor = operator
        self.cp_manager = cp_manager
        self.cpt = cpt
        self.internal_cpts = internal_cpts

    def __call__(self, input_pimg: PipeImage) -> PipeImage:
        self.cp_manager.observe(input_pimg, self.cpt)
        for internal_cpt in self.internal_cpts:
            self.cp_manager.observe(input_pimg, internal_cpt)

        cpt_path = self.cp_manager.directory / input_pimg.name / self.cpt
        if not cpt_path.exists():
            input_pimg.save(cpt_path)
            info(f"{self}: {input_pimg.name} checkpoint {self.cpt} saved")

        return self.processor(input_pimg)
