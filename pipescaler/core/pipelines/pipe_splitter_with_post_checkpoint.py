#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info
from typing import Callable, Collection

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.pipe_image import PipeImage


class PipeSplitterWithPostCheckpoints:
    """Wraps a PipeProcessor to add checkpointing."""

    cpt: str
    internal_cpts: list[str]

    def __init__(
        self,
        splitter: Callable[[PipeImage], Collection[PipeImage]],
        cp_manager: CheckpointManagerBase,
        cpts: Collection[str],
        internal_cpts: list[str],
    ) -> None:
        self.splitter = splitter
        self.cp_manager = cp_manager
        self.cpts = cpts
        self.internal_cpts = internal_cpts

    def __call__(self, input_pimg: PipeImage) -> Collection[PipeImage]:
        for cpt in self.cpts:
            self.cp_manager.observe(input_pimg, cpt)
        for internal_cpt in self.internal_cpts:
            self.cp_manager.observe(input_pimg, internal_cpt)

        cpt_paths = [
            self.cp_manager.directory / input_pimg.name / cpt for cpt in self.cpts
        ]
        if all(cpt_path.exists() for cpt_path in cpt_paths):
            output_imgs = tuple(
                PipeImage(path=cpt_path, parents=input_pimg) for cpt_path in cpt_paths
            )
            info(f"{self}: {input_pimg.name} checkpoints {self.cpts} loaded")
        else:
            output_imgs = self.splitter(input_pimg)
            if not cpt_paths[0].parent.exists():
                cpt_paths[0].parent.mkdir(parents=True)
            for output_img, cpt_path in zip(output_imgs, cpt_paths):
                output_img.save(cpt_path)
                info(f"{self}: {input_pimg.name} checkpoint {cpt_path} saved")

        return output_imgs
