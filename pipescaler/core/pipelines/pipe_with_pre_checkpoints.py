#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info
from typing import Collection, Union

from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.pipe_with_checkpoints import PipeWithCheckpoints


class PipeWithPreCheckpoints(PipeWithCheckpoints):
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
        if not all(cpt_path.exists() for cpt_path in cpt_paths):
            for input_pimg, cpt, cpt_path in zip(input_pimgs, self.cpts, cpt_paths):
                input_pimg.save(cpt_path)
                info(f"{self}: {input_pimg.name} checkpoint {cpt} saved")

        return self.pipe_stage(*input_pimgs)
