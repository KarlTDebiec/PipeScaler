#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import info

from pipescaler.core.image import Merger
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.pipe_operator import PipeOperator


class PipeMerger(PipeOperator):
    def __init__(self, merger: Merger) -> None:
        self.merger = merger

    def __call__(self, *input_pimgs: PipeImage) -> PipeImage:
        input_imgs = tuple(img.image for img in input_pimgs)

        output_img = self.merger(*input_imgs)
        output_pimg = PipeImage(output_img, parents=input_pimgs)
        info(f"{self.merger}: {output_pimg.name} merged")

        return output_pimg
