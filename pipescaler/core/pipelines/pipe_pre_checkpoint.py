#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info

from pipescaler.core.pipelines import PipeOperatorWithCheckpoints
from pipescaler.core.pipelines.pipe_image import PipeImage


class PipePreCheckpoint(PipeOperatorWithCheckpoints):
    def __call__(self, input_pimg: PipeImage) -> PipeImage:
        self.cp_manager.observe(input_pimg, self.cpt)
        for internal_cpt in self.internal_cpts:
            self.cp_manager.observe(input_pimg, internal_cpt)

        cpt_path = self.cp_manager.directory / input_pimg.name / self.cpt
        if not cpt_path.exists():
            input_pimg.save(cpt_path)
            info(f"{self}: {input_pimg.name} checkpoint {self.cpt} saved")

        return self.operator(input_pimg)
