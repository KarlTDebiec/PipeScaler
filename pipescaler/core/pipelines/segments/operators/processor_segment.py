#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info

from pipescaler.core.image import Processor
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.segments.operator_segment import OperatorSegment


class ProcessorSegment(OperatorSegment):
    operator: Processor

    def __init__(self, operator: Processor) -> None:
        super().__init__(operator)

    def __call__(self, *input_pimgs: PipeImage) -> PipeImage:
        input_img = input_pimgs[0].image

        output_img = self.operator(input_img)
        output_pimg = PipeImage(output_img, parents=input_pimgs)
        info(f"{self.operator}: {output_pimg.name} processed")

        return output_pimg
