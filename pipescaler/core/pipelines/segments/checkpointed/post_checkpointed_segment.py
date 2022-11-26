#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info
from typing import Collection, Union

from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.segments.checkpointed_segment import CheckpointedSegment


class PreCheckpointedSegment(CheckpointedSegment):
    def __call__(
        self, *input_pimgs: PipeImage
    ) -> Union[PipeImage, Collection[PipeImage]]:
        for input_pimg in input_pimgs:
            for cpt in self.cpts:
                self.cp_manager.observe(input_pimg, cpt)
            for internal_cpt in self.internal_cpts:
                self.cp_manager.observe(input_pimg, internal_cpt)

        cpt_paths = [
            self.cp_manager.directory / input_pimg.name / cpt
            for input_pimg in input_pimgs
            for cpt in self.cpts
        ]
        if all(cpt_path.exists() for cpt_path in cpt_paths):
            output_pimgs = tuple(
                PipeImage(path=cpt_path, parents=input_pimgs) for cpt_path in cpt_paths
            )
            info(f"{self}: {input_pimgs[0].name} checkpoints {self.cpts} loaded")
        else:
            output_pimgs = self.segment(*input_pimgs)
            if not cpt_paths[0].parent.exists():
                cpt_paths[0].parent.mkdir(parents=True)
            if isinstance(output_pimgs, PipeImage):
                output_pimgs.save(cpt_paths[0])
                info(f"{self}: {output_pimgs.name} checkpoint {self.cpts[0]} saved")
            else:
                for output_pimg, cpt_path in zip(output_pimgs, cpt_paths):
                    output_pimg.save(cpt_path)
                    info(f"{self}: {output_pimg.name} checkpoint {cpt_path} saved")

        return output_pimgs
