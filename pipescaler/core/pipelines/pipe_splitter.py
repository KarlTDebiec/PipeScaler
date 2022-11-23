#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info

from pipescaler.core.image import Splitter
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.pipe_operator import PipeOperator


class PipeSplitter(PipeOperator):
    def __init__(self, splitter: Splitter) -> None:
        self.splitter = splitter

    def __call__(self, input_pimg: PipeImage) -> tuple[PipeImage, ...]:
        input_img = input_pimg.image

        output_imgs = self.splitter(input_img)
        output_pimgs = tuple(
            PipeImage(output_img, parents=input_pimg) for output_img in output_imgs
        )
        info(f"{self.splitter}: {input_pimg.name} split")

        return output_pimgs
