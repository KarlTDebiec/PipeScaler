#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info

from pipescaler.core.image import Processor
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.pipe_operator import PipeOperator


class PipeProcessor(PipeOperator):
    def __init__(self, processor: Processor) -> None:
        self.processor = processor

    def __call__(self, input_pimg: PipeImage) -> PipeImage:
        input_img = input_pimg.image

        output_img = self.processor(input_img)
        output_pimg = PipeImage(output_img, parents=input_pimg)
        info(f"{self.processor}: {output_pimg.name} processed")

        return output_pimg
