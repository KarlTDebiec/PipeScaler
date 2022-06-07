#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Functions for routing."""
from itertools import tee
from typing import Iterator, Sequence, Union

from PIL import Image

from pipescaler.core.pipe_image import PipeImage
from pipescaler.core.stage import Stage


def route(
    stage: Stage, inlets: Union[Iterator[PipeImage], Sequence[Iterator[PipeImage]]]
) -> Union[Iterator[PipeImage], tuple[Iterator[PipeImage]]]:
    if isinstance(inlets, Iterator):
        inlets = [inlets]

    def generator() -> Iterator[PipeImage]:
        for input_pipe_images in zip(*inlets):
            input_images = tuple(image.image for image in input_pipe_images)
            output_images = stage(*input_images)
            if isinstance(output_images, Image.Image):
                yield PipeImage(output_images, parents=input_pipe_images)
            else:
                yield [
                    PipeImage(output_image, parents=input_pipe_images)
                    for output_image in output_images
                ]

    if len(stage.outputs) == 1:
        return generator()

    generators = []
    tees = tee(generator(), len(stage.outputs))
    for i, outlet in enumerate(stage.outputs.keys()):
        generators.append(eval(f"(elem[{i}] for elem in tees[{i}])"))
    return tuple(generators)
