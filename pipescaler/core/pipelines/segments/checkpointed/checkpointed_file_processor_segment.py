#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info

from pipescaler.common import get_temp_file_path
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.segments.checkpointed_segment import CheckpointedSegment
from pipescaler.core.pipelines.segments.file_processor_segment import (
    FileProcessorSegment,
)


class CheckpointedFileProcessorSegment(CheckpointedSegment):
    segment: FileProcessorSegment

    def __call__(self, *input_pimgs: PipeImage) -> PipeImage:
        input_pimg = input_pimgs[0]
        cpt = self.cpts[0]
        self.cp_manager.observe(input_pimg, cpt)

        cpt_path = self.cp_manager.directory / input_pimg.name / cpt
        if cpt_path.exists():
            output_pimg = PipeImage(path=cpt_path, parents=input_pimg)
            info(f"{self}: {output_pimg.name} checkpoint {cpt} loaded")
        else:
            if not cpt_path.parent.exists():
                cpt_path.parent.mkdir(parents=True)
            if input_pimg.path is None:
                with get_temp_file_path(".png") as input_path:
                    input_pimg.image.save(input_path)
                    self.segment.file_processor(input_path, cpt_path)
            else:
                self.segment.file_processor(input_pimg.path, cpt_path)
            output_pimg = PipeImage(path=cpt_path, parents=input_pimg)
            info(f"{self}: {input_pimg.name} checkpoint {cpt} saved")

        return output_pimg
