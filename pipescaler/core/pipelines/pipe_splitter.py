#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info
from typing import Collection

from pipescaler.core.image import Splitter
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.pipe_operator import PipeOperator


class PipeSplitter(PipeOperator):
    operator: Splitter

    def __init__(self, operator: Splitter) -> None:
        super().__init__(operator)

    def __call__(self, *input_pimgs: PipeImage) -> Collection[PipeImage]:
        input_img = input_pimgs[0].image

        output_imgs = self.operator(input_img)
        output_pimgs = tuple(
            PipeImage(output_img, parents=input_pimgs) for output_img in output_imgs
        )
        info(f"{self.operator}: {input_pimgs[0].name} split")

        return output_pimgs
